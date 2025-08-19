"""Engine and Studio management commands for DHT CLI."""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import boto3
import requests
import typer
from botocore.exceptions import ClientError, NoCredentialsError
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

# Initialize Typer apps
engine_app = typer.Typer(help="Manage compute engines for development.")
studio_app = typer.Typer(help="Manage persistent development studios.")

console = Console()

# Cost information
HOURLY_COSTS = {
    "cpu": 0.50,  # r6i.2xlarge
    "cpumax": 2.02,  # r7i.8xlarge
    "t4": 0.75,  # g4dn.2xlarge
    "a10g": 1.50,  # g5.2xlarge
    "a100": 21.96,  # p4d.24xlarge
    "4_t4": 3.91,  # g4dn.12xlarge
    "8_t4": 7.83,  # g4dn.metal
    "4_a10g": 6.24,  # g5.12xlarge
    "8_a10g": 16.29,  # g5.48xlarge
}

# SSH config management
SSH_MANAGED_COMMENT = "# Managed by dh engine"

# --------------------------------------------------------------------------------
# Bootstrap stage helpers
# --------------------------------------------------------------------------------


def _colour_stage(stage: str) -> str:
    """Return colourised stage name for table output."""
    if not stage:
        return "[dim]-[/dim]"
    low = stage.lower()
    if low.startswith("error"):
        return f"[red]{stage}[/red]"
    if low == "finished":
        return f"[green]{stage}[/green]"
    return f"[yellow]{stage}[/yellow]"


def _fetch_init_stages(instance_ids: List[str]) -> Dict[str, str]:
    """Fetch DayhoffInitStage tag for many instances in one call."""
    if not instance_ids:
        return {}
    ec2 = boto3.client("ec2", region_name="us-east-1")
    stages: Dict[str, str] = {}
    try:
        paginator = ec2.get_paginator("describe_instances")
        for page in paginator.paginate(InstanceIds=instance_ids):
            for res in page["Reservations"]:
                for inst in res["Instances"]:
                    iid = inst["InstanceId"]
                    tag_val = next(
                        (
                            t["Value"]
                            for t in inst.get("Tags", [])
                            if t["Key"] == "DayhoffInitStage"
                        ),
                        None,
                    )
                    if tag_val:
                        stages[iid] = tag_val
    except Exception:
        pass  # best-effort
    return stages


def check_aws_sso() -> str:
    """Check AWS SSO status and return username."""
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        # Parse username from assumed role ARN
        # Format: arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_DeveloperAccess_xxxx/username
        arn = identity["Arn"]
        if "assumed-role" in arn:
            username = arn.split("/")[-1]
            return username
        else:
            # Fallback for other auth methods
            return identity["UserId"].split(":")[-1]
    except (NoCredentialsError, ClientError):
        console.print("[red]❌ Not logged in to AWS SSO[/red]")
        console.print("Please run: [cyan]aws sso login[/cyan]")
        if Confirm.ask("Would you like to login now?"):
            try:
                result = subprocess.run(
                    ["aws", "sso", "login"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                if result.returncode == 0:
                    console.print("[green]✓ Successfully logged in![/green]")
                    return check_aws_sso()
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Login failed: {e}[/red]")
        raise typer.Exit(1)


def get_api_url() -> str:
    """Get Studio Manager API URL from SSM Parameter Store."""
    ssm = boto3.client("ssm", region_name="us-east-1")
    try:
        response = ssm.get_parameter(Name="/dev/studio-manager/api-url")
        return response["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            console.print(
                "[red]❌ API URL parameter not found in SSM Parameter Store[/red]"
            )
            console.print(
                "Please ensure the Studio Manager infrastructure is deployed."
            )
        else:
            console.print(f"[red]❌ Error retrieving API URL: {e}[/red]")
        raise typer.Exit(1)


def make_api_request(
    method: str,
    endpoint: str,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None,
) -> requests.Response:
    """Make an API request with error handling."""
    api_url = get_api_url()
    url = f"{api_url}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        return response
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ API request failed: {e}[/red]")
        raise typer.Exit(1)


def format_duration(duration: timedelta) -> str:
    """Format a duration as a human-readable string."""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def get_disk_usage_via_ssm(instance_id: str) -> Optional[str]:
    """Get disk usage for an engine via SSM.

    Returns:
        String like "17/50 GB" or None if failed
    """
    try:
        ssm = boto3.client("ssm", region_name="us-east-1")

        # Run df command to get disk usage
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    # Get root filesystem usage in GB
                    'df -BG / | tail -1 | awk \'{gsub(/G/, "", $2); gsub(/G/, "", $3); print $3 "/" $2 " GB"}\''
                ],
                "executionTimeout": ["10"],
            },
        )

        command_id = response["Command"]["CommandId"]

        # Wait for command to complete (with timeout)
        for _ in range(5):  # 5 second timeout
            time.sleep(1)
            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )
            if result["Status"] in ["Success", "Failed"]:
                break

        if result["Status"] == "Success":
            output = result["StandardOutputContent"].strip()
            return output if output else None

        return None

    except Exception as e:
        # logger.debug(f"Failed to get disk usage for {instance_id}: {e}") # Original code had this line commented out
        return None


def get_studio_disk_usage_via_ssm(instance_id: str, username: str) -> Optional[str]:
    """Get disk usage for a studio via SSM.

    Returns:
        String like "333/500 GB" or None if failed
    """
    try:
        ssm = boto3.client("ssm", region_name="us-east-1")

        # Run df command to get studio disk usage
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    # Get studio filesystem usage in GB
                    f'df -BG /studios/{username} 2>/dev/null | tail -1 | awk \'{{gsub(/G/, "", $2); gsub(/G/, "", $3); print $3 "/" $2 " GB"}}\''
                ],
                "executionTimeout": ["10"],
            },
        )

        command_id = response["Command"]["CommandId"]

        # Wait for command to complete (with timeout)
        for _ in range(5):  # 5 second timeout
            time.sleep(1)
            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )
            if result["Status"] in ["Success", "Failed"]:
                break

        if result["Status"] == "Success":
            output = result["StandardOutputContent"].strip()
            return output if output else None

        return None

    except Exception:
        return None


def parse_launch_time(launch_time_str: str) -> datetime:
    """Parse launch time from API response."""
    # Try different datetime formats
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",  # ISO format with timezone
        "%Y-%m-%dT%H:%M:%S+00:00",  # Explicit UTC offset
        "%Y-%m-%d %H:%M:%S",
    ]

    # First try parsing with fromisoformat for better timezone handling
    try:
        # Handle the ISO format properly
        return datetime.fromisoformat(launch_time_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        pass

    # Fallback to manual format parsing
    for fmt in formats:
        try:
            parsed = datetime.strptime(launch_time_str, fmt)
            # If no timezone info, assume UTC
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue

    # Fallback: assume it's recent
    return datetime.now(timezone.utc)


def format_status(state: str, ready: Optional[bool]) -> str:
    """Format engine status with ready indicator."""
    if state.lower() == "running":
        if ready is True:
            return "[green]Running ✓[/green]"
        elif ready is False:
            return "[yellow]Running ⚠ (Bootstrapping...)[/yellow]"
        else:
            return "[green]Running[/green]"
    elif state.lower() == "stopped":
        return "[dim]Stopped[/dim]"
    elif state.lower() == "stopping":
        return "[yellow]Stopping...[/yellow]"
    elif state.lower() == "pending":
        return "[yellow]Starting...[/yellow]"
    else:
        return state


# --------------------------------------------------------------------------------
# Audit helpers (Phase 1 observability)
# --------------------------------------------------------------------------------


def _get_engine_audit_bucket() -> Optional[str]:
    """Return the engine audit bucket name from SSM Parameter Store, if configured."""
    try:
        ssm = boto3.client("ssm", region_name="us-east-1")
        resp = ssm.get_parameter(Name="/dev/studio-manager/engine-audit-bucket")
        return resp["Parameter"]["Value"]
    except ClientError:
        return None


def _fetch_last_audit_via_ssm(instance_id: str) -> Optional[Dict]:
    """Fetch last shutdown attempt audit from the engine via SSM (fast best-effort)."""
    try:
        ssm = boto3.client("ssm", region_name="us-east-1")
        resp = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    "cat /var/log/idle-detector/last_shutdown_attempt.json 2>/dev/null || true",
                ],
                "executionTimeout": ["3"],
            },
        )
        cid = resp["Command"]["CommandId"]
        time.sleep(1)
        inv = ssm.get_command_invocation(CommandId=cid, InstanceId=instance_id)
        if inv["Status"] != "Success":
            return None
        content = inv["StandardOutputContent"].strip()
        if not content:
            return None
        return json.loads(content)
    except Exception:
        return None


def _fetch_last_audit_via_s3(instance_id: str) -> Optional[Dict]:
    """Fetch the newest audit object from S3 if available."""
    bucket = _get_engine_audit_bucket()
    if not bucket:
        return None
    try:
        s3 = boto3.client("s3", region_name="us-east-1")
        paginator = s3.get_paginator("list_objects_v2")
        newest = None
        for page in paginator.paginate(
            Bucket=bucket, Prefix=f"{instance_id}/", MaxKeys=1000
        ):
            for obj in page.get("Contents", []):
                lm = obj.get("LastModified")
                if newest is None or (lm and lm > newest["LastModified"]):
                    newest = obj
        if not newest:
            return None
        obj = s3.get_object(Bucket=bucket, Key=newest["Key"])
        data = obj["Body"].read().decode("utf-8")
        return json.loads(data)
    except Exception:
        return None


def _summarize_audit(audit: Dict) -> str:
    """Return a compact one-line summary for status output."""
    ts = audit.get("ts", "?")
    shutdown = audit.get("shutdown", {})
    result = shutdown.get("result", "?")
    detach = audit.get("detach", {})
    num_detached = sum(
        1 for r in detach.get("results", []) if r.get("status") == "success"
    )
    idle = audit.get("idle", {})
    elapsed = int(idle.get("elapsed_sec", 0))
    threshold = int(idle.get("threshold_sec", 0))
    return f"Last shutdown attempt: {ts} result={result} detach={num_detached} idle={elapsed//60}/{threshold//60}m"


def resolve_engine(name_or_id: str, engines: List[Dict]) -> Dict:
    """Resolve engine by name or ID with interactive selection."""
    # Exact ID match
    exact_id = [e for e in engines if e["instance_id"] == name_or_id]
    if exact_id:
        return exact_id[0]

    # Exact name match
    exact_name = [e for e in engines if e["name"] == name_or_id]
    if len(exact_name) == 1:
        return exact_name[0]

    # Prefix matches
    matches = [
        e
        for e in engines
        if e["name"].startswith(name_or_id) or e["instance_id"].startswith(name_or_id)
    ]

    if len(matches) == 0:
        console.print(f"[red]❌ No engine found matching '{name_or_id}'[/red]")
        raise typer.Exit(1)
    elif len(matches) == 1:
        return matches[0]
    else:
        # Interactive selection
        console.print(f"Multiple engines match '{name_or_id}':")
        for i, engine in enumerate(matches, 1):
            cost = HOURLY_COSTS.get(engine["engine_type"], 0)
            console.print(
                f"  {i}. [cyan]{engine['name']}[/cyan] ({engine['instance_id']}) "
                f"- {engine['engine_type']} - {engine['state']} - ${cost:.2f}/hr"
            )

        while True:
            try:
                choice = IntPrompt.ask(
                    "Select engine",
                    default=1,
                    choices=[str(i) for i in range(1, len(matches) + 1)],
                )
                return matches[choice - 1]
            except (ValueError, IndexError):
                console.print("[red]Invalid selection, please try again[/red]")


def get_ssh_public_key() -> str:
    """Get the user's SSH public key.

    Discovery order (container-friendly):
    1) DHT_SSH_PUBLIC_KEY env var (direct key content)
    2) DHT_SSH_PUBLIC_KEY_PATH env var (path to a .pub file)
    3) ssh-agent via `ssh-add -L` (requires SSH_AUTH_SOCK)
    4) Conventional files: ~/.ssh/id_ed25519.pub, ~/.ssh/id_rsa.pub

    Raises:
        FileNotFoundError: If no public key can be discovered.
    """
    # 1) Direct env var content
    env_key = os.environ.get("DHT_SSH_PUBLIC_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 2) Env var path
    env_path = os.environ.get("DHT_SSH_PUBLIC_KEY_PATH")
    if env_path:
        p = Path(env_path).expanduser()
        if p.is_file():
            try:
                return p.read_text().strip()
            except Exception:
                pass

    # 3) Agent lookup (ssh-add -L)
    try:
        if shutil.which("ssh-add") is not None:
            proc = subprocess.run(["ssh-add", "-L"], capture_output=True, text=True)
            if proc.returncode == 0 and proc.stdout:
                keys = [
                    line.strip() for line in proc.stdout.splitlines() if line.strip()
                ]
                # Prefer ed25519, then rsa
                for pref in ("ssh-ed25519", "ssh-rsa", "ecdsa-sha2-nistp256"):
                    for k in keys:
                        if k.startswith(pref + " "):
                            return k
                # Fallback to first key if types not matched
                if keys:
                    return keys[0]
    except Exception:
        pass

    # 4) Conventional files
    home = Path.home()
    key_paths = [home / ".ssh" / "id_ed25519.pub", home / ".ssh" / "id_rsa.pub"]
    for key_path in key_paths:
        if key_path.is_file():
            try:
                return key_path.read_text().strip()
            except Exception:
                continue

    raise FileNotFoundError(
        "No SSH public key found. Please create one with 'ssh-keygen' first."
    )


def check_session_manager_plugin():
    """Check if AWS Session Manager Plugin is available and warn if not."""
    if shutil.which("session-manager-plugin") is None:
        console.print(
            "[bold red]⚠️  AWS Session Manager Plugin not found![/bold red]\n"
            "SSH connections to engines require the Session Manager Plugin.\n"
            "Please install it following the setup guide:\n"
            "[link]https://github.com/dayhofflabs/nutshell/blob/main/REFERENCE/setup_guides/new-laptop.md[/link]"
        )
        return False
    return True


def update_ssh_config_entry(
    engine_name: str, instance_id: str, ssh_user: str, idle_timeout: int = 600
):
    """Add or update a single SSH config entry for the given SSH user.

    Args:
        engine_name:  Host alias to write into ~/.ssh/config
        instance_id:  EC2 instance-id (used by the proxy command)
        ssh_user:     Username to place into the SSH stanza
        idle_timeout: Idle timeout **in seconds** to pass to the SSM port-forward. 600 = 10 min.
    """
    config_path = Path.home() / ".ssh" / "config"
    config_path.parent.mkdir(mode=0o700, exist_ok=True)

    # Touch the file if it doesn't exist
    if not config_path.exists():
        config_path.touch(mode=0o600)

    # Read existing config
    content = config_path.read_text()
    lines = content.splitlines() if content else []

    # Remove any existing entry for this engine
    new_lines = []
    skip_until_next_host = False
    for line in lines:
        # Check if this is our managed host
        if (
            line.strip().startswith(f"Host {engine_name}")
            and SSH_MANAGED_COMMENT in line
        ):
            skip_until_next_host = True
        elif line.strip().startswith("Host ") and skip_until_next_host:
            skip_until_next_host = False
            # This is a different host entry, keep it
            new_lines.append(line)
        elif not skip_until_next_host:
            new_lines.append(line)

    # Add the new entry
    if new_lines and new_lines[-1].strip():  # Add blank line if needed
        new_lines.append("")

    new_lines.extend(
        [
            f"Host {engine_name} {SSH_MANAGED_COMMENT}",
            f"    HostName {instance_id}",
            f"    User {ssh_user}",
            f"    ProxyCommand sh -c \"AWS_SSM_IDLE_TIMEOUT={idle_timeout} aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'\"",
        ]
    )

    # Write back
    config_path.write_text("\n".join(new_lines))
    config_path.chmod(0o600)


# ==================== ENGINE COMMANDS ====================


@engine_app.command("launch")
def launch_engine(
    name: str = typer.Argument(help="Name for the new engine"),
    engine_type: str = typer.Option(
        "cpu",
        "--type",
        "-t",
        help="Engine type: cpu, cpumax, t4, a10g, a100, 4_t4, 8_t4, 4_a10g, 8_a10g",
    ),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Override username"),
    boot_disk_size: Optional[int] = typer.Option(
        None,
        "--size",
        "-s",
        help="Boot disk size in GB (default: 50GB, min: 20GB, max: 1000GB)",
    ),
    availability_zone: Optional[str] = typer.Option(
        None,
        "--az",
        help="Prefer a specific Availability Zone (e.g., us-east-1b). If omitted the service will try all public subnets.",
    ),
):
    """Launch a new engine instance."""
    username = check_aws_sso()
    if user:
        username = user

    # Validate engine type
    valid_types = [
        "cpu",
        "cpumax",
        "t4",
        "a10g",
        "a100",
        "4_t4",
        "8_t4",
        "4_a10g",
        "8_a10g",
    ]
    if engine_type not in valid_types:
        console.print(f"[red]❌ Invalid engine type: {engine_type}[/red]")
        console.print(f"Valid types: {', '.join(valid_types)}")
        raise typer.Exit(1)

    # Validate boot disk size
    if boot_disk_size is not None:
        if boot_disk_size < 20:
            console.print("[red]❌ Boot disk size must be at least 20GB[/red]")
            raise typer.Exit(1)
        if boot_disk_size > 1000:
            console.print("[red]❌ Boot disk size cannot exceed 1000GB[/red]")
            raise typer.Exit(1)

    cost = HOURLY_COSTS.get(engine_type, 0)
    disk_info = f" with {boot_disk_size}GB boot disk" if boot_disk_size else ""
    console.print(
        f"Launching [cyan]{name}[/cyan] ({engine_type}){disk_info} for ${cost:.2f}/hour..."
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Creating engine...", total=None)

        request_data = {
            "name": name,
            "user": username,
            "engine_type": engine_type,
        }
        if boot_disk_size is not None:
            request_data["boot_disk_size"] = boot_disk_size
        if availability_zone:
            request_data["availability_zone"] = availability_zone

        response = make_api_request("POST", "/engines", json_data=request_data)

    if response.status_code == 201:
        data = response.json()
        console.print(f"[green]✓ Engine launched successfully![/green]")
        console.print(f"Instance ID: [cyan]{data['instance_id']}[/cyan]")
        console.print(f"Type: {data['instance_type']} (${cost:.2f}/hour)")
        if boot_disk_size:
            console.print(f"Boot disk: {boot_disk_size}GB")
        console.print("\nThe engine is initializing. This may take a few minutes.")
        console.print(f"Check status with: [cyan]dh engine status {name}[/cyan]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to launch engine: {error}[/red]")


@engine_app.command("list")
def list_engines(
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Filter by user"),
    running_only: bool = typer.Option(
        False, "--running", help="Show only running engines"
    ),
    stopped_only: bool = typer.Option(
        False, "--stopped", help="Show only stopped engines"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed status (slower)"
    ),
):
    """List engines (shows all engines by default)."""
    current_user = check_aws_sso()

    params = {}
    if user:
        params["user"] = user
    if detailed:
        params["check_ready"] = "true"

    response = make_api_request("GET", "/engines", params=params)

    if response.status_code == 200:
        data = response.json()
        engines = data.get("engines", [])

        # Filter by state if requested
        if running_only:
            engines = [e for e in engines if e["state"].lower() == "running"]
        elif stopped_only:
            engines = [e for e in engines if e["state"].lower() == "stopped"]

        if not engines:
            console.print("No engines found.")
            return

        # Only fetch detailed info if requested (slow)
        stages_map = {}
        if detailed:
            stages_map = _fetch_init_stages([e["instance_id"] for e in engines])

        # Create table
        table = Table(title="Engines", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Instance ID", style="dim")
        table.add_column("Type")
        table.add_column("User")
        table.add_column("Status")
        if detailed:
            table.add_column("Disk Usage")
        table.add_column("Uptime/Since")
        table.add_column("$/hour", justify="right")

        for engine in engines:
            launch_time = parse_launch_time(engine["launch_time"])
            uptime = datetime.now(timezone.utc) - launch_time
            hourly_cost = HOURLY_COSTS.get(engine["engine_type"], 0)

            if engine["state"].lower() == "running":
                time_str = format_duration(uptime)
                # Only get disk usage if detailed mode
                if detailed:
                    disk_usage = get_disk_usage_via_ssm(engine["instance_id"]) or "-"
                else:
                    disk_usage = None
            else:
                time_str = launch_time.strftime("%Y-%m-%d %H:%M")
                disk_usage = "-" if detailed else None

            row_data = [
                engine["name"],
                engine["instance_id"],
                engine["engine_type"],
                engine["user"],
                format_status(engine["state"], engine.get("ready")),
            ]
            if detailed:
                row_data.append(disk_usage)
            row_data.extend(
                [
                    time_str,
                    f"${hourly_cost:.2f}",
                ]
            )

            table.add_row(*row_data)

        console.print(table)
        if not detailed and any(e["state"].lower() == "running" for e in engines):
            console.print(
                "\n[dim]Tip: Use --detailed to see disk usage and bootstrap status (slower)[/dim]"
            )
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to list engines: {error}[/red]")


@engine_app.command("status")
def engine_status(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    show_log: bool = typer.Option(False, "--show-log", help="Show bootstrap log"),
):
    """Show detailed engine status and information."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    # Get detailed engine status including idle detector info
    response = make_api_request("GET", f"/engines/{engine['instance_id']}")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engine details[/red]")
        raise typer.Exit(1)

    engine_details = response.json()
    engine = engine_details.get("engine", engine)  # Use detailed info if available
    idle_detector = engine_details.get("idle_detector", {})
    attached_studios = engine_details.get("attached_studios", [])

    # Calculate costs
    launch_time = parse_launch_time(engine["launch_time"])
    uptime = datetime.now(timezone.utc) - launch_time
    hourly_cost = HOURLY_COSTS.get(engine["engine_type"], 0)
    total_cost = hourly_cost * (uptime.total_seconds() / 3600)

    stages_map = _fetch_init_stages([engine["instance_id"]])
    stage_val = stages_map.get(engine["instance_id"], "-")

    status_lines = [
        f"[bold]Name:[/bold]        {engine['name']}",
        f"[bold]Instance:[/bold]    {engine['instance_id']}",
        f"[bold]Type:[/bold]        {engine['engine_type']} ({engine['instance_type']})",
        f"[bold]Status:[/bold]      {format_status(engine['state'], engine.get('ready'))}",
        f"[bold]User:[/bold]        {engine['user']}",
        f"[bold]IP:[/bold]          {engine.get('public_ip', 'N/A')}",
        f"[bold]Launched:[/bold]    {launch_time.strftime('%Y-%m-%d %H:%M:%S')} ({format_duration(uptime)} ago)",
        f"[bold]Cost:[/bold]        ${hourly_cost:.2f}/hour (${total_cost:.2f} total)",
    ]

    # Health report (only if bootstrap finished)
    if stage_val == "finished":
        try:
            ssm = boto3.client("ssm", region_name="us-east-1")
            res = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [
                        "cat /opt/dayhoff/state/engine-health.json 2>/dev/null || cat /var/run/engine-health.json 2>/dev/null || true"
                    ],
                    "executionTimeout": ["10"],
                },
            )
            cid = res["Command"]["CommandId"]
            time.sleep(1)
            inv = ssm.get_command_invocation(
                CommandId=cid, InstanceId=engine["instance_id"]
            )
            if inv["Status"] == "Success":
                import json as _json

                health = _json.loads(inv["StandardOutputContent"].strip() or "{}")
                status_lines.append("")
                status_lines.append("[bold]Health:[/bold]")
                status_lines.append(
                    f"  • GPU Drivers: {'OK' if health.get('drivers_ok') else 'MISSING'}"
                )
                status_lines.append(
                    f"  • Idle Detector: {health.get('idle_detector_timer', 'unknown')}"
                )
        except Exception:
            pass

    # Idle detector status (from new API endpoint)
    if idle_detector.get("available"):
        status_lines.append("")
        status_lines.append("[bold]Idle Detector:[/bold]")

        # Overall status
        if idle_detector["status"] == "active":
            status_lines.append("  [green]✓ Engine ACTIVE[/green]")
        else:
            idle_seconds = idle_detector.get("idle_seconds", 0)
            idle_threshold = idle_detector.get("idle_threshold", 1800)
            idle_minutes = idle_seconds // 60
            threshold_minutes = idle_threshold // 60
            status_lines.append(
                f"  [yellow]⏱ Engine IDLE ({idle_minutes}/{threshold_minutes} minutes)[/yellow]"
            )

        # Coffee lock
        if idle_detector.get("coffee_lock"):
            status_lines.append(
                f"  • [cyan]☕ Caffeinated for another {idle_detector['coffee_lock']}[/cyan]"
            )

        # SSH sessions
        ssh_sessions = idle_detector.get("ssh_sessions", [])
        if ssh_sessions:
            status_lines.append(f"  • [blue]SSH Sessions ({len(ssh_sessions)}):[/blue]")
            for session in ssh_sessions:
                status_lines.append(
                    f"    - {session['tty']} (pid {session['pid']}, idle {session['idle_time']}) from {session['from_ip']}"
                )

        # IDE connections
        ide_conn = idle_detector.get("ide_connections")
        if ide_conn:
            status_lines.append(
                f"  • [magenta]🖥  IDE connected ({ide_conn['connection_count']} connections)[/magenta]"
            )

    # Audit one-liner (best-effort SSM fetch)
    try:
        last_audit = _fetch_last_audit_via_ssm(engine["instance_id"])
        if last_audit:
            status_lines.append("")
            status_lines.append("[bold]Idle Audit:[/bold]")
            status_lines.append(f"  • {_summarize_audit(last_audit)}")
    except Exception:
        pass

    if attached_studios:
        status_lines.append("")
        status_lines.append("[bold]Attached Studios:[/bold]")
        for studio in attached_studios:
            status_lines.append(f"  • {studio['user']} ({studio['studio_id']})")

    console.print(
        Panel("\n".join(status_lines), title="Engine Status", border_style="blue")
    )

    if show_log:
        console.print("\n[bold]Bootstrap Log:[/bold]")
        try:
            ssm = boto3.client("ssm", region_name="us-east-1")
            resp = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [
                        "cat /var/log/engine-setup.log 2>/dev/null || echo 'No setup log found'"
                    ],
                    "executionTimeout": ["15"],
                },
            )
            cid = resp["Command"]["CommandId"]
            time.sleep(2)
            inv = ssm.get_command_invocation(
                CommandId=cid, InstanceId=engine["instance_id"]
            )
            if inv["Status"] == "Success":
                log_content = inv["StandardOutputContent"].strip()
                if log_content:
                    console.print(f"[dim]{log_content}[/dim]")
                else:
                    console.print("[yellow]No bootstrap log available[/yellow]")
            else:
                console.print("[red]❌ Could not retrieve bootstrap log[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error fetching log: {e}[/red]")


@engine_app.command("why")
def engine_why(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    raw: bool = typer.Option(False, "--raw", help="Print raw audit JSON"),
):
    """Explain the last idle-detector shutdown attempt for an engine.

    Tries SSM (on-instance file) first, then falls back to S3 audit bucket.
    """
    check_aws_sso()

    # Resolve engine
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    audit = _fetch_last_audit_via_ssm(
        engine["instance_id"]
    ) or _fetch_last_audit_via_s3(engine["instance_id"])
    if not audit:
        console.print("No audit found (engine may not have attempted shutdown yet).")
        raise typer.Exit(0)

    if raw:
        console.print_json(data=audit)
        return

    # Pretty summary
    status = _summarize_audit(audit)
    panel_lines = [
        f"[bold]{status}[/bold]",
        "",
        "[bold]Sensors:[/bold]",
    ]
    for r in audit.get("idle", {}).get("reason_snapshot", []):
        active = "✓" if r.get("active") else "-"
        reason = r.get("reason") or ""
        sensor = r.get("sensor")
        panel_lines.append(f"  {active} {sensor}: {reason}")
    panel_lines.append("")
    panel_lines.append("[bold]Detach results:[/bold]")
    for res in audit.get("detach", {}).get("results", []):
        panel_lines.append(
            f"  - {res.get('studio_id')}: {res.get('status')} {res.get('error') or ''}"
        )
    s3_info = audit.get("s3", {})
    if s3_info.get("uploaded"):
        panel_lines.append("")
        panel_lines.append(
            f"[dim]S3: s3://{s3_info.get('bucket')}/{s3_info.get('key')}[/dim]"
        )

    console.print(
        Panel("\n".join(panel_lines), title="Idle Shutdown Audit", border_style="blue")
    )


@engine_app.command("stop")
def stop_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force stop and detach all studios"
    ),
):
    """Stop an engine."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    console.print(f"Stopping engine [cyan]{engine['name']}[/cyan]...")

    # First attempt without detaching
    response = make_api_request(
        "POST",
        f"/engines/{engine['instance_id']}/stop",
        json_data={"detach_studios": force},
    )

    if response.status_code == 409 and not force:
        # Engine has attached studios
        data = response.json()
        attached_studios = data.get("attached_studios", [])

        console.print("\n[yellow]⚠️  This engine has attached studios:[/yellow]")
        for studio in attached_studios:
            console.print(f"  • {studio['user']} ({studio['studio_id']})")

        if Confirm.ask("\nDetach all studios and stop the engine?"):
            response = make_api_request(
                "POST",
                f"/engines/{engine['instance_id']}/stop",
                json_data={"detach_studios": True},
            )
        else:
            console.print("Stop cancelled.")
            return

    if response.status_code == 200:
        console.print(f"[green]✓ Engine stopped successfully![/green]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to stop engine: {error}[/red]")


@engine_app.command("start")
def start_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
):
    """Start a stopped engine."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    console.print(f"Starting engine [cyan]{engine['name']}[/cyan]...")

    response = make_api_request("POST", f"/engines/{engine['instance_id']}/start")

    if response.status_code == 200:
        data = response.json()
        console.print(f"[green]✓ Engine started successfully![/green]")
        console.print(f"New public IP: {data.get('public_ip', 'Pending...')}")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to start engine: {error}[/red]")


@engine_app.command("terminate")
def terminate_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
):
    """Permanently terminate an engine."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    # Calculate cost
    launch_time = parse_launch_time(engine["launch_time"])
    uptime = datetime.now(timezone.utc) - launch_time
    hourly_cost = HOURLY_COSTS.get(engine["engine_type"], 0)
    total_cost = hourly_cost * (uptime.total_seconds() / 3600)

    console.print(
        f"\n[yellow]⚠️  This will permanently terminate engine '{engine['name']}'[/yellow]"
    )
    console.print(f"Total cost for this session: ${total_cost:.2f}")

    if not Confirm.ask("\nAre you sure you want to terminate this engine?"):
        console.print("Termination cancelled.")
        return

    response = make_api_request("DELETE", f"/engines/{engine['instance_id']}")

    if response.status_code == 200:
        console.print(f"[green]✓ Engine terminated successfully![/green]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to terminate engine: {error}[/red]")


@engine_app.command("ssh")
def ssh_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    admin: bool = typer.Option(
        False, "--admin", help="Connect as ec2-user instead of the engine owner user"
    ),
    idle_timeout: int = typer.Option(
        600,
        "--idle-timeout",
        help="Idle timeout (seconds) for the SSM port-forward (0 = disable)",
    ),
):
    """Connect to an engine via SSH.

    By default the CLI connects using the engine's owner username (the same one stored in the `User` tag).
    Pass `--admin` to connect with the underlying [`ec2-user`] account for break-glass or debugging.
    """
    username = check_aws_sso()

    # Check for Session Manager Plugin
    if not check_session_manager_plugin():
        raise typer.Exit(1)

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    if engine["state"].lower() != "running":
        console.print(f"[red]❌ Engine is not running (state: {engine['state']})[/red]")
        raise typer.Exit(1)

    # Choose SSH user
    ssh_user = "ec2-user" if admin else username

    # Update SSH config
    console.print(
        f"Updating SSH config for [cyan]{engine['name']}[/cyan] (user: {ssh_user})..."
    )
    update_ssh_config_entry(
        engine["name"], engine["instance_id"], ssh_user, idle_timeout
    )

    # Connect
    console.print(f"[green]✓ Connecting to {engine['name']}...[/green]")
    subprocess.run(["ssh", engine["name"]])


@engine_app.command("config-ssh")
def config_ssh(
    clean: bool = typer.Option(False, "--clean", help="Remove all managed entries"),
    all_engines: bool = typer.Option(
        False, "--all", "-a", help="Include all engines from all users"
    ),
    admin: bool = typer.Option(
        False,
        "--admin",
        help="Generate entries that use ec2-user instead of per-engine owner user",
    ),
):
    """Update SSH config with available engines."""
    username = check_aws_sso()

    # Only check for Session Manager Plugin if we're not just cleaning
    if not clean and not check_session_manager_plugin():
        raise typer.Exit(1)

    if clean:
        console.print("Removing all managed SSH entries...")
    else:
        if all_engines:
            console.print("Updating SSH config with all running engines...")
        else:
            console.print(
                f"Updating SSH config with running engines for [cyan]{username}[/cyan] and [cyan]shared[/cyan]..."
            )

    # Get all engines
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    running_engines = [e for e in engines if e["state"].lower() == "running"]

    # Filter engines based on options
    if not all_engines:
        # Show only current user's engines and shared engines
        running_engines = [
            e for e in running_engines if e["user"] == username or e["user"] == "shared"
        ]

    # Read existing config
    config_path = Path.home() / ".ssh" / "config"
    config_path.parent.mkdir(mode=0o700, exist_ok=True)

    if config_path.exists():
        content = config_path.read_text()
        lines = content.splitlines()
    else:
        content = ""
        lines = []

    # Remove old managed entries
    new_lines = []
    skip_until_next_host = False
    for line in lines:
        if SSH_MANAGED_COMMENT in line:
            skip_until_next_host = True
        elif line.strip().startswith("Host ") and skip_until_next_host:
            skip_until_next_host = False
            # Check if this is a managed host
            if SSH_MANAGED_COMMENT not in line:
                new_lines.append(line)
        elif not skip_until_next_host:
            new_lines.append(line)

    # Add new entries if not cleaning
    if not clean:
        for engine in running_engines:
            # Determine ssh user based on --admin flag
            ssh_user = "ec2-user" if admin else username
            new_lines.extend(
                [
                    "",
                    f"Host {engine['name']} {SSH_MANAGED_COMMENT}",
                    f"    HostName {engine['instance_id']}",
                    f"    User {ssh_user}",
                    f"    ProxyCommand sh -c \"AWS_SSM_IDLE_TIMEOUT=600 aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'\"",
                ]
            )

    # Write back
    config_path.write_text("\n".join(new_lines))
    config_path.chmod(0o600)

    if clean:
        console.print("[green]✓ Removed all managed SSH entries[/green]")
    else:
        console.print(
            f"[green]✓ Updated SSH config with {len(running_engines)} engines[/green]"
        )
        for engine in running_engines:
            user_display = (
                f"[dim]({engine['user']})[/dim]" if engine["user"] != username else ""
            )
            console.print(
                f"  • {engine['name']} → {engine['instance_id']} {user_display}"
            )


@engine_app.command("coffee")
def coffee(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    duration: str = typer.Argument("4h", help="Duration (e.g., 2h, 30m, 2h30m)"),
    cancel: bool = typer.Option(
        False, "--cancel", help="Cancel existing coffee lock instead of extending"
    ),
):
    """Pour ☕ for an engine: keeps it awake for the given duration (or cancel)."""
    username = check_aws_sso()

    # Parse duration
    import re

    if not cancel:
        match = re.match(r"(?:(\d+)h)?(?:(\d+)m)?", duration)
        if not match or (not match.group(1) and not match.group(2)):
            console.print(f"[red]❌ Invalid duration format: {duration}[/red]")
            console.print("Use format like: 4h, 30m, 2h30m")
            raise typer.Exit(1)

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds_total = (hours * 60 + minutes) * 60
        if seconds_total == 0:
            console.print("[red]❌ Duration must be greater than zero[/red]")
            raise typer.Exit(1)

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    if engine["state"].lower() != "running":
        console.print(f"[red]❌ Engine is not running (state: {engine['state']})[/red]")
        raise typer.Exit(1)

    if cancel:
        console.print(f"Cancelling coffee for [cyan]{engine['name']}[/cyan]…")
    else:
        console.print(
            f"Pouring coffee for [cyan]{engine['name']}[/cyan] for {duration}…"
        )

    # Use SSM to run the engine coffee command
    ssm = boto3.client("ssm", region_name="us-east-1")
    try:
        response = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    (
                        "/usr/local/bin/engine-coffee --cancel"
                        if cancel
                        else f"/usr/local/bin/engine-coffee {seconds_total}"
                    )
                ],
                "executionTimeout": ["60"],
            },
        )

        command_id = response["Command"]["CommandId"]

        # Wait for command to complete
        for _ in range(10):
            time.sleep(1)
            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=engine["instance_id"],
            )
            if result["Status"] in ["Success", "Failed"]:
                break

        if result["Status"] == "Success":
            if cancel:
                console.print(
                    "[green]✓ Coffee cancelled – auto-shutdown re-enabled[/green]"
                )
            else:
                console.print(f"[green]✓ Coffee poured for {duration}[/green]")
            console.print(
                "\n[dim]Note: Detached Docker containers (except dev containers) will also keep the engine awake.[/dim]"
            )
            console.print(
                "[dim]Use coffee for nohup operations or other background tasks.[/dim]"
            )
        else:
            console.print(
                f"[red]❌ Failed to manage coffee: {result.get('StatusDetails', 'Unknown error')}[/red]"
            )

    except ClientError as e:
        console.print(f"[red]❌ Failed to manage coffee: {e}[/red]")


@engine_app.command("resize")
def resize_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    size: int = typer.Option(..., "--size", "-s", help="New size in GB"),
    online: bool = typer.Option(
        False,
        "--online",
        help="Resize while running (requires manual filesystem expansion)",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force resize and detach all studios"
    ),
):
    """Resize an engine's boot disk."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    # Get current volume info to validate size
    ec2 = boto3.client("ec2", region_name="us-east-1")

    try:
        # Get instance details to find root volume
        instance_info = ec2.describe_instances(InstanceIds=[engine["instance_id"]])
        instance = instance_info["Reservations"][0]["Instances"][0]

        # Find root volume
        root_device = instance.get("RootDeviceName", "/dev/xvda")
        root_volume_id = None

        for bdm in instance.get("BlockDeviceMappings", []):
            if bdm["DeviceName"] == root_device:
                root_volume_id = bdm["Ebs"]["VolumeId"]
                break

        if not root_volume_id:
            console.print("[red]❌ Could not find root volume[/red]")
            raise typer.Exit(1)

        # Get current volume size
        volumes = ec2.describe_volumes(VolumeIds=[root_volume_id])
        current_size = volumes["Volumes"][0]["Size"]

        if size <= current_size:
            console.print(
                f"[red]❌ New size ({size}GB) must be larger than current size ({current_size}GB)[/red]"
            )
            raise typer.Exit(1)

        console.print(
            f"[yellow]Resizing engine boot disk from {current_size}GB to {size}GB[/yellow]"
        )

        # Check if we need to stop the instance
        if not online and engine["state"].lower() == "running":
            console.print("Stopping engine for offline resize...")
            stop_response = make_api_request(
                "POST",
                f"/engines/{engine['instance_id']}/stop",
                json_data={"detach_studios": False},
            )
            if stop_response.status_code != 200:
                console.print("[red]❌ Failed to stop engine[/red]")
                raise typer.Exit(1)

            # Wait for instance to stop
            console.print("Waiting for engine to stop...")
            waiter = ec2.get_waiter("instance_stopped")
            waiter.wait(InstanceIds=[engine["instance_id"]])
            console.print("[green]✓ Engine stopped[/green]")

        # Call the resize API
        console.print("Resizing volume...")
        resize_response = make_api_request(
            "POST",
            f"/engines/{engine['instance_id']}/resize",
            json_data={"size": size, "detach_studios": force},
        )

        if resize_response.status_code == 409 and not force:
            # Engine has attached studios
            data = resize_response.json()
            attached_studios = data.get("attached_studios", [])

            console.print("\n[yellow]⚠️  This engine has attached studios:[/yellow]")
            for studio in attached_studios:
                console.print(f"  • {studio['user']} ({studio['studio_id']})")

            if Confirm.ask("\nDetach all studios and resize the engine?"):
                resize_response = make_api_request(
                    "POST",
                    f"/engines/{engine['instance_id']}/resize",
                    json_data={"size": size, "detach_studios": True},
                )
            else:
                console.print("Resize cancelled.")
                return

        if resize_response.status_code != 200:
            error = resize_response.json().get("error", "Unknown error")
            console.print(f"[red]❌ Failed to resize engine: {error}[/red]")
            raise typer.Exit(1)

        # Check if studios were detached
        data = resize_response.json()
        detached_studios = data.get("detached_studios", 0)
        if detached_studios > 0:
            console.print(
                f"[green]✓ Detached {detached_studios} studio(s) before resize[/green]"
            )

        # Wait for modification to complete
        console.print("Waiting for volume modification to complete...")
        while True:
            mod_state = ec2.describe_volumes_modifications(VolumeIds=[root_volume_id])
            if not mod_state["VolumesModifications"]:
                break  # Modification complete

            modification = mod_state["VolumesModifications"][0]
            state = modification["ModificationState"]
            progress = modification.get("Progress", 0)

            # Show progress updates only for the resize phase
            if state == "modifying":
                console.print(f"[yellow]Progress: {progress}%[/yellow]")

            # Exit as soon as optimization starts (resize is complete)
            if state == "optimizing":
                console.print("[green]✓ Volume resized successfully[/green]")
                console.print(
                    "[dim]AWS is optimizing the volume in the background (no action needed).[/dim]"
                )
                break

            if state == "completed":
                console.print("[green]✓ Volume resized successfully[/green]")
                break
            elif state == "failed":
                console.print("[red]❌ Volume modification failed[/red]")
                raise typer.Exit(1)

            time.sleep(2)  # Check more frequently for better UX

        # If offline resize, start the instance back up
        if not online and engine["state"].lower() == "running":
            console.print("Starting engine back up...")
            start_response = make_api_request(
                "POST", f"/engines/{engine['instance_id']}/start"
            )
            if start_response.status_code != 200:
                console.print(
                    "[yellow]⚠️  Failed to restart engine automatically[/yellow]"
                )
                console.print(
                    f"Please start it manually: [cyan]dh engine start {engine['name']}[/cyan]"
                )
            else:
                console.print("[green]✓ Engine started[/green]")
                console.print("The filesystem will be automatically expanded on boot.")

        elif online and engine["state"].lower() == "running":
            console.print(
                "\n[yellow]⚠️  Online resize complete. You must now expand the filesystem:[/yellow]"
            )
            console.print(f"1. SSH into the engine: [cyan]ssh {engine['name']}[/cyan]")
            console.print("2. Find the root device: [cyan]lsblk[/cyan]")
            console.print(
                "3. Expand the partition: [cyan]sudo growpart /dev/nvme0n1 1[/cyan] (adjust device name as needed)"
            )
            console.print("4. Expand the filesystem: [cyan]sudo xfs_growfs /[/cyan]")

    except ClientError as e:
        console.print(f"[red]❌ Failed to resize engine: {e}[/red]")
        raise typer.Exit(1)


@engine_app.command("gami")
def create_ami(
    name_or_id: str = typer.Argument(
        help="Engine name or instance ID to create AMI from"
    ),
):
    """Create a 'Golden AMI' from a running engine.

    This process is for creating a pre-warmed, standardized machine image
    that can be used to launch new engines more quickly.

    IMPORTANT:
    - The engine MUST have all studios detached before running this command.
    - This process will make the source engine unusable. You should
      plan to TERMINATE the engine after the AMI is created.
    """
    check_aws_sso()

    # Get all engines to resolve name and check status
    # We pass check_ready=True to get attached studio info
    response = make_api_request("GET", "/engines", params={"check_ready": "true"})
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    # --- Pre-flight checks ---

    # 1. Check if engine is running
    if engine["state"].lower() != "running":
        console.print(f"[red]❌ Engine '{engine['name']}' is not running.[/red]")
        console.print("Please start it before creating an AMI.")
        raise typer.Exit(1)

    # 2. Check for attached studios from the detailed API response
    attached_studios = engine.get("studios", [])
    if attached_studios:
        console.print(
            f"[bold red]❌ Engine '{engine['name']}' has studios attached.[/bold red]"
        )
        console.print("Please detach all studios before creating an AMI:")
        for studio in attached_studios:
            console.print(f"  - {studio['user']} ({studio['studio_id']})")
        console.print("\nTo detach, run [bold]dh studio detach[/bold]")
        raise typer.Exit(1)

    # Construct AMI name and description
    ami_name = (
        f"prewarmed-engine-{engine['engine_type']}-{datetime.now().strftime('%Y%m%d')}"
    )
    description = (
        f"Amazon Linux 2023 with NVIDIA drivers, Docker, and pre-pulled "
        f"dev container image for {engine['engine_type']} engines"
    )

    console.print(f"Creating AMI from engine [cyan]{engine['name']}[/cyan]...")
    console.print(f"[bold]AMI Name:[/] {ami_name}")
    console.print(f"[bold]Description:[/] {description}")

    console.print(
        "\n[bold yellow]⚠️  Important:[/bold yellow]\n"
        "1. This process will run cleanup scripts on the engine.\n"
        "2. The source engine should be [bold]terminated[/bold] after the AMI is created.\n"
    )

    if not Confirm.ask("Continue with AMI creation?"):
        raise typer.Exit()

    # Create AMI using EC2 client directly, as the backend logic is too complex
    ec2 = boto3.client("ec2", region_name="us-east-1")
    ssm = boto3.client("ssm", region_name="us-east-1")

    try:
        # Clean up instance state before snapshotting
        console.print("Cleaning up instance for AMI creation...")
        cleanup_commands = [
            "sudo rm -f /opt/dayhoff/first_boot_complete.sentinel",
            "history -c",
            "sudo rm -rf /tmp/* /var/log/messages /var/log/cloud-init.log",
            "sudo rm -rf /var/lib/amazon/ssm/* /etc/amazon/ssm/*",
            "sleep 2 && sudo systemctl stop amazon-ssm-agent &",  # Stop agent last
        ]

        cleanup_response = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": cleanup_commands, "executionTimeout": ["120"]},
        )

        # Acknowledge that the SSM command might be in progress as the agent shuts down
        console.print(
            "[dim]ℹ️  Cleanup command sent (status may show 'InProgress' as SSM agent stops)[/dim]"
        )

        # Create the AMI
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                "Creating AMI (this will take several minutes)...", total=None
            )

            response = ec2.create_image(
                InstanceId=engine["instance_id"],
                Name=ami_name,
                Description=description,
                NoReboot=False,
                TagSpecifications=[
                    {
                        "ResourceType": "image",
                        "Tags": [
                            {"Key": "Environment", "Value": "dev"},
                            {"Key": "Type", "Value": "golden-ami"},
                            {"Key": "EngineType", "Value": engine["engine_type"]},
                            {"Key": "Name", "Value": ami_name},
                        ],
                    }
                ],
            )

            ami_id = response["ImageId"]
            progress.update(
                task,
                completed=True,
                description=f"[green]✓ AMI creation initiated![/green]",
            )

        console.print(f"  [bold]AMI ID:[/] {ami_id}")
        console.print("\nThe AMI creation process will continue in the background.")
        console.print("You can monitor progress in the EC2 Console under 'AMIs'.")
        console.print(
            "\nOnce complete, update the AMI ID in [bold]terraform/environments/dev/variables.tf[/bold] "
            "and run [bold]terraform apply[/bold]."
        )
        console.print(
            f"\nRemember to [bold red]terminate the source engine '{engine['name']}'[/bold red] to save costs."
        )

    except ClientError as e:
        console.print(f"[red]❌ Failed to create AMI: {e}[/red]")
        raise typer.Exit(1)


# ==================== STUDIO COMMANDS ====================


def get_user_studio(username: str) -> Optional[Dict]:
    """Get the current user's studio."""
    response = make_api_request("GET", "/studios")
    if response.status_code != 200:
        return None

    studios = response.json().get("studios", [])
    user_studios = [s for s in studios if s["user"] == username]

    return user_studios[0] if user_studios else None


@studio_app.command("create")
def create_studio(
    size_gb: int = typer.Option(50, "--size", "-s", help="Studio size in GB"),
):
    """Create a new studio for the current user."""
    username = check_aws_sso()

    # Check if user already has a studio
    existing = get_user_studio(username)
    if existing:
        console.print(
            f"[yellow]You already have a studio: {existing['studio_id']}[/yellow]"
        )
        return

    console.print(f"Creating {size_gb}GB studio for user [cyan]{username}[/cyan]...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Creating studio volume...", total=None)

        response = make_api_request(
            "POST",
            "/studios",
            json_data={"user": username, "size_gb": size_gb},
        )

    if response.status_code == 201:
        data = response.json()
        console.print(f"[green]✓ Studio created successfully![/green]")
        console.print(f"Studio ID: [cyan]{data['studio_id']}[/cyan]")
        console.print(f"Size: {data['size_gb']}GB")
        console.print(f"\nNext step: [cyan]dh studio attach <engine-name>[/cyan]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to create studio: {error}[/red]")


@studio_app.command("status")
def studio_status(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Check status for a different user (admin only)"
    ),
):
    """Show status of your studio."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add warning when checking another user's studio
    if target_user != username:
        console.print(
            f"[yellow]⚠️  Checking studio status for user: {target_user}[/yellow]"
        )

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio yet.[/yellow]")
            console.print("Create one with: [cyan]dh studio create[/cyan]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    # Create status panel
    # Format status with colors
    status = studio["status"]
    if status == "in-use":
        status_display = "[bright_blue]attached[/bright_blue]"
    elif status in ["attaching", "detaching"]:
        status_display = f"[yellow]{status}[/yellow]"
    else:
        status_display = f"[green]{status}[/green]"

    status_lines = [
        f"[bold]Studio ID:[/bold]    {studio['studio_id']}",
        f"[bold]User:[/bold]         {studio['user']}",
        f"[bold]Status:[/bold]       {status_display}",
        f"[bold]Size:[/bold]         {studio['size_gb']}GB",
        f"[bold]Created:[/bold]      {studio['creation_date']}",
    ]

    if studio.get("attached_vm_id"):
        status_lines.append(f"[bold]Attached to:[/bold]  {studio['attached_vm_id']}")

        # Try to get engine details
        response = make_api_request("GET", "/engines")
        if response.status_code == 200:
            engines = response.json().get("engines", [])
            attached_engine = next(
                (e for e in engines if e["instance_id"] == studio["attached_vm_id"]),
                None,
            )
            if attached_engine:
                status_lines.append(
                    f"[bold]Engine Name:[/bold]  {attached_engine['name']}"
                )

    panel = Panel(
        "\n".join(status_lines),
        title="Studio Details",
        border_style="blue",
    )
    console.print(panel)


def _is_studio_attached(target_studio_id: str, target_vm_id: str) -> bool:
    """Return True when the given studio already shows as attached to the VM.

    Using this extra check lets us stop the outer retry loop as soon as the
    asynchronous attach operation actually finishes, even in the unlikely
    event that the operation-tracking DynamoDB record is not yet updated.
    """
    # First try the per-studio endpoint – fastest.
    resp = make_api_request("GET", f"/studios/{target_studio_id}")
    if resp.status_code == 200:
        data = resp.json()
        if (
            data.get("status") == "in-use"
            and data.get("attached_vm_id") == target_vm_id
        ):
            return True
    # Fallback: list + filter (covers edge-cases where the direct endpoint
    # is slower to update IAM/APIGW mapping than the list endpoint).
    list_resp = make_api_request("GET", "/studios")
    if list_resp.status_code == 200:
        for stu in list_resp.json().get("studios", []):
            if (
                stu.get("studio_id") == target_studio_id
                and stu.get("status") == "in-use"
                and stu.get("attached_vm_id") == target_vm_id
            ):
                return True
    return False


@studio_app.command("attach")
def attach_studio(
    engine_name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Attach a different user's studio (admin only)"
    ),
):
    """Attach your studio to an engine."""
    username = check_aws_sso()

    # Check for Session Manager Plugin since we'll update SSH config
    if not check_session_manager_plugin():
        raise typer.Exit(1)

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add confirmation when attaching another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Managing studio for user: {target_user}[/yellow]")
        if not Confirm.ask(f"Are you sure you want to attach {target_user}'s studio?"):
            console.print("Operation cancelled.")
            return

    # Get user's studio
    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio yet.[/yellow]")
            if Confirm.ask("Would you like to create one now?"):
                size = IntPrompt.ask("Studio size (GB)", default=50)
                response = make_api_request(
                    "POST",
                    "/studios",
                    json_data={"user": username, "size_gb": size},
                )
                if response.status_code != 201:
                    console.print("[red]❌ Failed to create studio[/red]")
                    raise typer.Exit(1)
                studio = response.json()
                studio["studio_id"] = studio["studio_id"]  # Normalize key
            else:
                raise typer.Exit(0)
        else:
            console.print(f"[red]❌ User {target_user} doesn't have a studio.[/red]")
            raise typer.Exit(1)

    # Check if already attached
    if studio.get("status") == "in-use":
        console.print(
            f"[yellow]Studio is already attached to {studio.get('attached_vm_id')}[/yellow]"
        )
        if not Confirm.ask("Detach and reattach to new engine?"):
            return
        # Detach first
        response = make_api_request("POST", f"/studios/{studio['studio_id']}/detach")
        if response.status_code != 200:
            console.print("[red]❌ Failed to detach studio[/red]")
            raise typer.Exit(1)

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(engine_name_or_id, engines)

    # Flag to track if we started the engine in this command (affects retry length)
    engine_started_now: bool = False

    if engine["state"].lower() != "running":
        console.print(f"[yellow]⚠️  Engine is {engine['state']}[/yellow]")
        if engine["state"].lower() == "stopped" and Confirm.ask(
            "Start the engine first?"
        ):
            response = make_api_request(
                "POST", f"/engines/{engine['instance_id']}/start"
            )
            if response.status_code != 200:
                console.print("[red]❌ Failed to start engine[/red]")
                raise typer.Exit(1)
            console.print("[green]✓ Engine started[/green]")
            # Mark that we booted the engine so attach loop gets extended retries
            engine_started_now = True
            # No further waiting here – attachment attempts below handle retry logic while the
            # engine finishes booting.
        else:
            raise typer.Exit(1)

    # Retrieve SSH public key (required for authorised_keys provisioning)
    try:
        public_key = get_ssh_public_key()
    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)

    console.print(f"Attaching studio to engine [cyan]{engine['name']}[/cyan]...")

    # Determine retry strategy based on whether we just started the engine
    if engine_started_now:
        max_attempts = 40  # About 7 minutes total with exponential backoff
        base_delay = 8
        max_delay = 20
    else:
        max_attempts = 15  # About 2 minutes total with exponential backoff
        base_delay = 5
        max_delay = 10

    # Unified retry loop with exponential backoff
    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as prog:
        desc = (
            "Attaching studio (engine is still booting)…"
            if engine_started_now
            else "Attaching studio…"
        )
        task = prog.add_task(desc, total=None)

        consecutive_not_ready = 0
        last_error = None

        for attempt in range(max_attempts):
            # Check if the attach already completed
            if _is_studio_attached(studio["studio_id"], engine["instance_id"]):
                success = True
                break

            success, error_msg = _attempt_studio_attach(
                studio, engine, target_user, public_key
            )

            if success:
                break  # success!

            if error_msg:
                # Fatal error – bubble up immediately
                console.print(f"[red]❌ Failed to attach studio: {error_msg}[/red]")

                # Suggest repair command if engine seems broken
                if "not ready" in error_msg.lower() and attempt > 5:
                    console.print(
                        f"\n[yellow]Engine may be in a bad state. Try:[/yellow]"
                    )
                    console.print(f"[dim]  dh engine repair {engine['name']}[/dim]")
                return

            # Track consecutive "not ready" responses
            consecutive_not_ready += 1
            last_error = "Engine not ready"

            # Update progress display
            if attempt % 3 == 0:
                prog.update(
                    task,
                    description=f"{desc} attempt {attempt+1}/{max_attempts}",
                )

            # If engine seems stuck after many attempts, show a hint
            if consecutive_not_ready > 10 and attempt == 10:
                console.print(
                    "[yellow]Engine is taking longer than expected to become ready.[/yellow]"
                )
                console.print(
                    "[dim]This can happen after GAMI creation or if the engine is still bootstrapping.[/dim]"
                )

            # Exponential backoff with jitter
            delay = min(base_delay * (1.5 ** min(attempt, 5)), max_delay)
            delay += time.time() % 2  # Add 0-2 seconds of jitter
            time.sleep(delay)

        else:
            # All attempts exhausted
            console.print(
                f"[yellow]Engine is not becoming ready after {max_attempts} attempts.[/yellow]"
            )
            if last_error:
                console.print(f"[dim]Last issue: {last_error}[/dim]")
            console.print("\n[yellow]You can try:[/yellow]")
            console.print(
                f"  1. Wait a minute and retry: [cyan]dh studio attach {engine['name']}[/cyan]"
            )
            console.print(
                f"  2. Check engine status: [cyan]dh engine status {engine['name']}[/cyan]"
            )
            console.print(
                f"  3. Repair the engine: [cyan]dh engine repair {engine['name']}[/cyan]"
            )
            return

    # Successful attach path
    console.print(f"[green]✓ Studio attached successfully![/green]")

    # Update SSH config - use target_user for the connection
    update_ssh_config_entry(engine["name"], engine["instance_id"], target_user)
    console.print(f"[green]✓ SSH config updated[/green]")
    console.print(f"\nConnect with: [cyan]ssh {engine['name']}[/cyan]")
    console.print(f"Files are at: [cyan]/studios/{target_user}[/cyan]")


def _attempt_studio_attach(studio, engine, target_user, public_key):
    response = make_api_request(
        "POST",
        f"/studios/{studio['studio_id']}/attach",
        json_data={
            "vm_id": engine["instance_id"],
            "user": target_user,
            "public_key": public_key,
        },
    )

    # Fast-path success
    if response.status_code == 200:
        return True, None

    # Asynchronous path – API returned 202 Accepted and operation tracking ID
    if response.status_code == 202:
        # The operation status polling is broken in the Lambda, so we just
        # wait and check if the studio is actually attached
        time.sleep(5)  # Give the async operation a moment to start

        # Check periodically if the studio is attached
        for check in range(20):  # Check for up to 60 seconds
            if _is_studio_attached(studio["studio_id"], engine["instance_id"]):
                return True, None
            time.sleep(3)

        # If we get here, attachment didn't complete in reasonable time
        return False, None  # Return None to trigger retry

    # --- determine if we should retry ---
    recoverable = False
    error_text = response.json().get("error", "Unknown error")
    err_msg = error_text.lower()

    # Check for "Studio is not available (status: in-use)" which means it's already attached
    if (
        response.status_code == 400
        and "not available" in err_msg
        and "in-use" in err_msg
    ):
        # Studio is already attached somewhere - check if it's to THIS engine
        if _is_studio_attached(studio["studio_id"], engine["instance_id"]):
            return True, None  # It's attached to our target engine - success!
        else:
            return False, error_text  # It's attached elsewhere - fatal error

    if response.status_code in (409, 503):
        recoverable = True
    else:
        RECOVERABLE_PATTERNS = [
            "not ready",
            "still starting",
            "initializing",
            "failed to mount",
            "device busy",
            "pending",  # VM state pending
        ]
        FATAL_PATTERNS = [
            "permission",
        ]
        if any(p in err_msg for p in FATAL_PATTERNS):
            recoverable = False
        elif any(p in err_msg for p in RECOVERABLE_PATTERNS):
            recoverable = True

    if not recoverable:
        # fatal – abort immediately
        return False, error_text

    # recoverable – signal caller to retry without treating as error
    return False, None


# Note: _poll_operation was removed because the Lambda's operation tracking is broken.
# We now use _is_studio_attached() to check if the studio is actually attached instead.


@studio_app.command("detach")
def detach_studio(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Detach a different user's studio (admin only)"
    ),
):
    """Detach your studio from its current engine."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add confirmation when detaching another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Managing studio for user: {target_user}[/yellow]")
        if not Confirm.ask(f"Are you sure you want to detach {target_user}'s studio?"):
            console.print("Operation cancelled.")
            return

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio.[/yellow]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    if studio.get("status") != "in-use":
        if target_user == username:
            console.print("[yellow]Your studio is not attached to any engine.[/yellow]")
        else:
            console.print(
                f"[yellow]{target_user}'s studio is not attached to any engine.[/yellow]"
            )
        return

    console.print(f"Detaching studio from {studio.get('attached_vm_id')}...")

    response = make_api_request("POST", f"/studios/{studio['studio_id']}/detach")

    if response.status_code == 200:
        console.print(f"[green]✓ Studio detached successfully![/green]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to detach studio: {error}[/red]")


@studio_app.command("delete")
def delete_studio(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Delete a different user's studio (admin only)"
    ),
):
    """Delete your studio permanently."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Extra warning when deleting another user's studio
    if target_user != username:
        console.print(
            f"[red]⚠️  ADMIN ACTION: Deleting studio for user: {target_user}[/red]"
        )

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio to delete.[/yellow]")
        else:
            console.print(
                f"[yellow]User {target_user} doesn't have a studio to delete.[/yellow]"
            )
        return

    console.print(
        "[red]⚠️  WARNING: This will permanently delete the studio and all data![/red]"
    )
    console.print(f"Studio ID: {studio['studio_id']}")
    console.print(f"User: {target_user}")
    console.print(f"Size: {studio['size_gb']}GB")

    # Multiple confirmations
    if not Confirm.ask(
        f"\nAre you sure you want to delete {target_user}'s studio?"
        if target_user != username
        else "\nAre you sure you want to delete your studio?"
    ):
        console.print("Deletion cancelled.")
        return

    if not Confirm.ask("[red]This action cannot be undone. Continue?[/red]"):
        console.print("Deletion cancelled.")
        return

    typed_confirm = Prompt.ask('Type "DELETE" to confirm permanent deletion')
    if typed_confirm != "DELETE":
        console.print("Deletion cancelled.")
        return

    response = make_api_request("DELETE", f"/studios/{studio['studio_id']}")

    if response.status_code == 200:
        console.print(f"[green]✓ Studio deleted successfully![/green]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to delete studio: {error}[/red]")


@studio_app.command("list")
def list_studios(
    all_users: bool = typer.Option(
        False, "--all", "-a", help="Show all users' studios"
    ),
):
    """List studios."""
    username = check_aws_sso()

    response = make_api_request("GET", "/studios")

    if response.status_code == 200:
        studios = response.json().get("studios", [])

        if not studios:
            console.print("No studios found.")
            return

        # Get all engines to map instance IDs to names
        engines_response = make_api_request("GET", "/engines")
        engines = {}
        if engines_response.status_code == 200:
            for engine in engines_response.json().get("engines", []):
                engines[engine["instance_id"]] = engine["name"]

        # Create table
        table = Table(title="Studios", box=box.ROUNDED)
        table.add_column("Studio ID", style="cyan")
        table.add_column("User")
        table.add_column("Status")
        table.add_column("Size", justify="right")
        table.add_column("Disk Usage", justify="right")
        table.add_column("Attached To")

        for studio in studios:
            # Change status display
            if studio["status"] == "in-use":
                status_display = "[bright_blue]attached[/bright_blue]"
            elif studio["status"] in ["attaching", "detaching"]:
                status_display = "[yellow]" + studio["status"] + "[/yellow]"
            else:
                status_display = "[green]available[/green]"

            # Format attached engine info
            attached_to = "-"
            disk_usage = "?/?"
            if studio.get("attached_vm_id"):
                vm_id = studio["attached_vm_id"]
                engine_name = engines.get(vm_id, "unknown")
                attached_to = f"{engine_name} ({vm_id})"

                # Try to get disk usage if attached
                if studio["status"] == "in-use":
                    usage = get_studio_disk_usage_via_ssm(vm_id, studio["user"])
                    if usage:
                        disk_usage = usage

            table.add_row(
                studio["studio_id"],
                studio["user"],
                status_display,
                f"{studio['size_gb']}GB",
                disk_usage,
                attached_to,
            )

        console.print(table)
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to list studios: {error}[/red]")


@studio_app.command("reset")
def reset_studio(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Reset a different user's studio"
    ),
):
    """Reset a stuck studio (admin operation)."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add warning when resetting another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Resetting studio for user: {target_user}[/yellow]")

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio.[/yellow]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    console.print(f"[yellow]⚠️  This will force-reset the studio state[/yellow]")
    console.print(f"Current status: {studio['status']}")
    if studio.get("attached_vm_id"):
        console.print(f"Listed as attached to: {studio['attached_vm_id']}")

    if not Confirm.ask("\nReset studio state?"):
        console.print("Reset cancelled.")
        return

    # Direct DynamoDB update
    console.print("Resetting studio state...")

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("dev-studios")

    try:
        # Check if volume is actually attached
        ec2 = boto3.client("ec2", region_name="us-east-1")
        volumes = ec2.describe_volumes(VolumeIds=[studio["studio_id"]])

        if volumes["Volumes"]:
            volume = volumes["Volumes"][0]
            attachments = volume.get("Attachments", [])
            if attachments:
                console.print(
                    f"[red]Volume is still attached to {attachments[0]['InstanceId']}![/red]"
                )
                if Confirm.ask("Force-detach the volume?"):
                    ec2.detach_volume(
                        VolumeId=studio["studio_id"],
                        InstanceId=attachments[0]["InstanceId"],
                        Force=True,
                    )
                    console.print("Waiting for volume to detach...")
                    waiter = ec2.get_waiter("volume_available")
                    waiter.wait(VolumeIds=[studio["studio_id"]])

        # Reset in DynamoDB – align attribute names with Studio Manager backend
        table.update_item(
            Key={"StudioID": studio["studio_id"]},
            UpdateExpression="SET #st = :status, AttachedVMID = :vm_id, AttachedDevice = :device",
            ExpressionAttributeNames={"#st": "Status"},
            ExpressionAttributeValues={
                ":status": "available",
                ":vm_id": None,
                ":device": None,
            },
        )

        console.print(f"[green]✓ Studio reset to available state![/green]")

    except ClientError as e:
        console.print(f"[red]❌ Failed to reset studio: {e}[/red]")


@studio_app.command("resize")
def resize_studio(
    size: int = typer.Option(..., "--size", "-s", help="New size in GB"),
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Resize a different user's studio (admin only)"
    ),
):
    """Resize your studio volume (requires detachment)."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add warning when resizing another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Resizing studio for user: {target_user}[/yellow]")

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio yet.[/yellow]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    current_size = studio["size_gb"]

    if size <= current_size:
        console.print(
            f"[red]❌ New size ({size}GB) must be larger than current size ({current_size}GB)[/red]"
        )
        raise typer.Exit(1)

    # Check if studio is attached
    if studio["status"] == "in-use":
        console.print("[yellow]⚠️  Studio must be detached before resizing[/yellow]")
        console.print(f"Currently attached to: {studio.get('attached_vm_id')}")

        if not Confirm.ask("\nDetach studio and proceed with resize?"):
            console.print("Resize cancelled.")
            return

        # Detach the studio
        console.print("Detaching studio...")
        response = make_api_request("POST", f"/studios/{studio['studio_id']}/detach")
        if response.status_code != 200:
            console.print("[red]❌ Failed to detach studio[/red]")
            raise typer.Exit(1)

        console.print("[green]✓ Studio detached[/green]")

        # Wait a moment for detachment to complete
        time.sleep(5)

    console.print(f"[yellow]Resizing studio from {current_size}GB to {size}GB[/yellow]")

    # Call the resize API
    resize_response = make_api_request(
        "POST", f"/studios/{studio['studio_id']}/resize", json_data={"size": size}
    )

    if resize_response.status_code != 200:
        error = resize_response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to resize studio: {error}[/red]")
        raise typer.Exit(1)

    # Wait for volume modification to complete
    ec2 = boto3.client("ec2", region_name="us-east-1")
    console.print("Resizing volume...")

    # Track progress
    last_progress = 0

    while True:
        try:
            mod_state = ec2.describe_volumes_modifications(
                VolumeIds=[studio["studio_id"]]
            )
            if not mod_state["VolumesModifications"]:
                break  # Modification complete

            modification = mod_state["VolumesModifications"][0]
            state = modification["ModificationState"]
            progress = modification.get("Progress", 0)

            # Show progress updates only for the resize phase
            if state == "modifying" and progress > last_progress:
                console.print(f"[yellow]Progress: {progress}%[/yellow]")
                last_progress = progress

            # Exit as soon as optimization starts (resize is complete)
            if state == "optimizing":
                console.print(
                    f"[green]✓ Studio resized successfully to {size}GB![/green]"
                )
                console.print(
                    "[dim]AWS is optimizing the volume in the background (no action needed).[/dim]"
                )
                break

            if state == "completed":
                console.print(
                    f"[green]✓ Studio resized successfully to {size}GB![/green]"
                )
                break
            elif state == "failed":
                console.print("[red]❌ Volume modification failed[/red]")
                raise typer.Exit(1)

            time.sleep(2)  # Check more frequently for better UX

        except ClientError:
            # Modification might be complete
            console.print(f"[green]✓ Studio resized successfully to {size}GB![/green]")
            break

    console.print(
        "\n[dim]The filesystem will be automatically expanded when you next attach the studio.[/dim]"
    )
    console.print(f"To attach: [cyan]dh studio attach <engine-name>[/cyan]")


# ================= Idle timeout command =================


@engine_app.command("idle")
def idle_timeout_cmd(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    set: Optional[str] = typer.Option(
        None, "--set", "-s", help="New timeout (e.g., 2h30m, 45m)"
    ),
):
    """Show or set the engine idle-detector timeout."""
    check_aws_sso()

    # Resolve engine
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    ssm = boto3.client("ssm", region_name="us-east-1")

    if set is None:
        # Show current
        resp = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    "grep -E '^IDLE_TIMEOUT_SECONDS=' /etc/engine.env || echo 'IDLE_TIMEOUT_SECONDS=1800'"
                ],
                "executionTimeout": ["10"],
            },
        )
        cid = resp["Command"]["CommandId"]
        time.sleep(1)
        inv = ssm.get_command_invocation(
            CommandId=cid, InstanceId=engine["instance_id"]
        )
        if inv["Status"] == "Success":
            line = inv["StandardOutputContent"].strip()
            secs = int(line.split("=")[1]) if "=" in line else 1800
            console.print(f"Current idle timeout: {secs//60}m ({secs} seconds)")
        else:
            console.print("[red]❌ Could not retrieve idle timeout[/red]")
        return

    # ----- set new value -----
    m = re.match(r"^(?:(\d+)h)?(?:(\d+)m)?$", set)
    if not m:
        console.print("[red]❌ Invalid duration format. Use e.g. 2h, 45m, 1h30m[/red]")
        raise typer.Exit(1)
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = hours * 3600 + minutes * 60
    if seconds == 0:
        console.print("[red]❌ Duration must be greater than zero[/red]")
        raise typer.Exit(1)

    console.print(f"Setting idle timeout to {set} ({seconds} seconds)…")

    cmd = (
        "sudo sed -i '/^IDLE_TIMEOUT_SECONDS=/d' /etc/engine.env && "
        f"echo 'IDLE_TIMEOUT_SECONDS={seconds}' | sudo tee -a /etc/engine.env >/dev/null && "
        "sudo systemctl restart engine-idle-detector.timer"
    )

    resp = ssm.send_command(
        InstanceIds=[engine["instance_id"]],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": [cmd], "executionTimeout": ["60"]},
    )
    cid = resp["Command"]["CommandId"]
    time.sleep(2)
    console.print(f"[green]✓ Idle timeout updated to {set}[/green]")


# Add this near the end, after the idle-timeout command


@engine_app.command("debug")
def debug_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
):
    """Debug engine bootstrap status and files."""
    check_aws_sso()

    # Resolve engine
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    console.print(f"[bold]Debug info for {engine['name']}:[/bold]\n")

    ssm = boto3.client("ssm", region_name="us-east-1")

    # Check multiple files and systemd status
    checks = [
        (
            "Stage file",
            "cat /opt/dayhoff/state/engine-init.stage 2>/dev/null || cat /var/run/engine-init.stage 2>/dev/null || echo 'MISSING'",
        ),
        (
            "Health file",
            "cat /opt/dayhoff/state/engine-health.json 2>/dev/null || cat /var/run/engine-health.json 2>/dev/null || echo 'MISSING'",
        ),
        (
            "Sentinel file",
            "ls -la /opt/dayhoff/first_boot_complete.sentinel 2>/dev/null || echo 'MISSING'",
        ),
        (
            "Setup service",
            "systemctl status setup-aws-vm.service --no-pager || echo 'Service not found'",
        ),
        (
            "Bootstrap log tail",
            "tail -20 /var/log/engine-setup.log 2>/dev/null || echo 'No log'",
        ),
        ("Environment file", "cat /etc/engine.env 2>/dev/null || echo 'MISSING'"),
    ]

    for name, cmd in checks:
        try:
            resp = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={"commands": [cmd], "executionTimeout": ["10"]},
            )
            cid = resp["Command"]["CommandId"]
            time.sleep(1)
            inv = ssm.get_command_invocation(
                CommandId=cid, InstanceId=engine["instance_id"]
            )

            if inv["Status"] == "Success":
                output = inv["StandardOutputContent"].strip()
                console.print(f"[cyan]{name}:[/cyan]")
                console.print(f"[dim]{output}[/dim]\n")
            else:
                console.print(f"[cyan]{name}:[/cyan] [red]FAILED[/red]\n")

        except Exception as e:
            console.print(f"[cyan]{name}:[/cyan] [red]ERROR: {e}[/red]\n")


@engine_app.command("repair")
def repair_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
):
    """Repair an engine that's stuck in a bad state (e.g., after GAMI creation)."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    if engine["state"].lower() != "running":
        console.print(
            f"[yellow]⚠️  Engine is {engine['state']}. Must be running to repair.[/yellow]"
        )
        if engine["state"].lower() == "stopped" and Confirm.ask(
            "Start the engine first?"
        ):
            response = make_api_request(
                "POST", f"/engines/{engine['instance_id']}/start"
            )
            if response.status_code != 200:
                console.print("[red]❌ Failed to start engine[/red]")
                raise typer.Exit(1)
            console.print("[green]✓ Engine started[/green]")
            console.print("Waiting for engine to become ready...")
            time.sleep(30)  # Give it time to boot
        else:
            raise typer.Exit(1)

    console.print(f"[bold]Repairing engine [cyan]{engine['name']}[/cyan][/bold]")
    console.print(
        "[dim]This will restore bootstrap state and ensure all services are running[/dim]\n"
    )

    ssm = boto3.client("ssm", region_name="us-east-1")

    # Repair commands
    repair_commands = [
        # Create necessary directories
        "sudo mkdir -p /opt/dayhoff /opt/dayhoff/state /opt/dayhoff/scripts",
        # Download scripts from S3 if missing
        "source /etc/engine.env && sudo aws s3 sync s3://${VM_SCRIPTS_BUCKET}/ /opt/dayhoff/scripts/ --exclude '*' --include '*.sh' --quiet",
        "sudo chmod +x /opt/dayhoff/scripts/*.sh 2>/dev/null || true",
        # Restore bootstrap state
        "sudo touch /opt/dayhoff/first_boot_complete.sentinel",
        "echo 'finished' | sudo tee /opt/dayhoff/state/engine-init.stage > /dev/null",
        # Ensure SSM agent is running
        "sudo systemctl restart amazon-ssm-agent 2>/dev/null || true",
        # Restart idle detector
        "sudo systemctl restart engine-idle-detector.timer 2>/dev/null || true",
        "sudo systemctl restart engine-idle-detector.service 2>/dev/null || true",
        # Report status
        "echo '=== Repair Complete ===' && echo 'Sentinel: ' && ls -la /opt/dayhoff/first_boot_complete.sentinel",
        "echo 'Stage: ' && cat /opt/dayhoff/state/engine-init.stage",
        "echo 'Scripts: ' && ls /opt/dayhoff/scripts/*.sh 2>/dev/null | wc -l",
    ]

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Repairing engine...", total=None)

            response = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": repair_commands,
                    "executionTimeout": ["60"],
                },
            )

            command_id = response["Command"]["CommandId"]

            # Wait for command
            for _ in range(60):
                time.sleep(1)
                result = ssm.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=engine["instance_id"],
                )
                if result["Status"] in ["Success", "Failed"]:
                    break

        if result["Status"] == "Success":
            output = result["StandardOutputContent"]
            console.print("[green]✓ Engine repaired successfully![/green]\n")

            # Show repair results
            if "=== Repair Complete ===" in output:
                repair_section = output.split("=== Repair Complete ===")[1].strip()
                console.print("[bold]Repair Results:[/bold]")
                console.print(repair_section)

            console.print(
                "\n[dim]You should now be able to attach studios to this engine.[/dim]"
            )
        else:
            console.print(
                f"[red]❌ Repair failed: {result.get('StandardErrorContent', 'Unknown error')}[/red]"
            )
            console.print(
                "\n[yellow]Try running 'dh engine debug' for more information.[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]❌ Failed to repair engine: {e}[/red]")
