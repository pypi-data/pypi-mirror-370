"""CLI commands common to all repos."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import toml
import typer
import yaml

# Import cloud helper lazily inside functions to avoid heavy deps at module load


def test_github_actions_locally():
    """Run the script test_pytest_in_github_actions_container.sh.sh."""
    script_path = ".devcontainer/scripts/test_pytest_in_github_actions_container.sh"

    try:
        subprocess.check_call(["bash", script_path])
        print("Script ran successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the script: {e}")


def delete_local_branch(branch_name: str, folder_path: str):
    """Delete a local Git branch after fetching with pruning.

    Args:
        branch_name: Name of the branch to delete
        folder_path: Path to the git repository folder
    """
    try:
        # Store current working directory
        original_dir = os.getcwd()

        # Change to the specified directory
        os.chdir(folder_path)
        print(f"Changed to directory: {folder_path}")

        # Delete the specified branch
        delete_branch_cmd = ["git", "branch", "-D", branch_name]
        subprocess.run(delete_branch_cmd, check=True)
        print(f"Deleted branch: {branch_name}")

        # Fetch changes from the remote repository and prune obsolete branches
        fetch_prune_cmd = ["git", "fetch", "-p"]
        subprocess.run(fetch_prune_cmd, check=True)
        print("Fetched changes and pruned obsolete branches")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Git commands: {e}")
    finally:
        # Always return to the original directory
        os.chdir(original_dir)


def get_current_version_from_toml(file_path="pyproject.toml"):
    """Reads the version from a pyproject.toml file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
        version_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if version_match:
            return version_match.group(1)
        else:
            raise ValueError(f"Could not find version string in {file_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"{file_path} not found.")
    except Exception as e:
        raise e


def build_and_upload_wheel(bump_part: str = "patch"):
    """Build a Python wheel and upload to PyPI using UV.

    Automatically increments the version number in pyproject.toml before building
    based on the bump_part argument ('major', 'minor', 'patch').

    Expects PyPI authentication to be configured via the environment variable:
    - UV_PUBLISH_TOKEN

    Args:
        bump_part (str): The part of the version to bump. Defaults to 'patch'.
    """
    if bump_part not in ["major", "minor", "patch"]:
        print(
            f"Error: Invalid bump_part '{bump_part}'. Must be 'major', 'minor', or 'patch'."
        )
        return

    # ANSI color codes
    BLUE = "\033[94m"
    RESET = "\033[0m"

    # --- Authentication Setup ---
    token = os.environ.get("UV_PUBLISH_TOKEN")

    if not token:
        print("Error: PyPI authentication not configured.")
        print(
            "Please set the UV_PUBLISH_TOKEN environment variable with your PyPI API token."
        )
        return

    # Build the command with token authentication
    # IMPORTANT: Mask token for printing
    publish_cmd_safe_print = ["uv", "publish", "--token", "*****"]
    publish_cmd = ["uv", "publish", "--token", token]
    print("Using UV_PUBLISH_TOKEN for authentication.")

    pyproject_path = "pyproject.toml"
    mac_manifest_path = "pyproject.mac.toml"
    current_version = None  # Initialize in case the first try block fails

    try:
        # --- Clean dist directory ---
        dist_dir = Path("dist")
        if dist_dir.exists():
            print(f"Removing existing build directory: {dist_dir}")
            shutil.rmtree(dist_dir)
        # --- End Clean dist directory ---

        # --- Version Bumping Logic ---
        current_version = get_current_version_from_toml(pyproject_path)
        print(f"Current version: {current_version}")

        try:
            major, minor, patch = map(int, current_version.split("."))
        except ValueError:
            print(
                f"Error: Could not parse version '{current_version}'. Expected format X.Y.Z"
            )
            return

        if bump_part == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_part == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        print(f"Bumping {bump_part} version to: {new_version}")

        # Read pyproject.toml
        with open(pyproject_path, "r") as f:
            content = f.read()

        # Replace the version string
        pattern = re.compile(
            f'^version\s*=\s*"{re.escape(current_version)}"', re.MULTILINE
        )
        new_content, num_replacements = pattern.subn(
            f'version = "{new_version}"', content
        )

        if num_replacements == 0:
            print(
                f"Error: Could not find 'version = \"{current_version}\"' in {pyproject_path}"
            )
            return  # Exit before build/publish if version wasn't updated
        if num_replacements > 1:
            print(
                f"Warning: Found multiple version lines for '{current_version}'. Only the first was updated."
            )

        # Write the updated content back
        with open(pyproject_path, "w") as f:
            f.write(new_content)
        print(f"Updated {pyproject_path} with version {new_version}")

        # Mirror version in pyproject.mac.toml if present (best-effort)
        mac_updated = False
        try:
            mac_path = Path(mac_manifest_path)
            if mac_path.exists():
                mac_content = mac_path.read_text()
                mac_pattern = re.compile(
                    f'^version\s*=\s*"{re.escape(current_version)}"', re.MULTILINE
                )
                mac_new_content, mac_replacements = mac_pattern.subn(
                    f'version = "{new_version}"', mac_content
                )
                if mac_replacements > 0:
                    mac_path.write_text(mac_new_content)
                    mac_updated = True
                    print(f"Updated {mac_manifest_path} with version {new_version}")
        except Exception as e:
            print(f"Warning: Could not update {mac_manifest_path}: {e}")
        # --- End Version Bumping Logic ---

        # Build wheel and sdist
        build_cmd = ["uv", "build"]
        # Print command in blue
        print(f"Running command: {BLUE}{' '.join(build_cmd)}{RESET}")
        subprocess.run(build_cmd, check=True)

        # Upload using uv publish with explicit arguments
        # Print masked command in blue
        print(f"Running command: {BLUE}{' '.join(publish_cmd_safe_print)}{RESET}")
        subprocess.run(
            publish_cmd,  # Use the actual command with token
            check=True,
        )

        print(f"Successfully built and uploaded version {new_version} to PyPI")

        # Re-install DHT in current venv when building from DHT itself
        try:
            proj_name = None
            try:
                proj_toml = toml.load(pyproject_path)
                proj_name = (
                    proj_toml.get("project", {}).get("name")
                    if isinstance(proj_toml, dict)
                    else None
                )
            except Exception:
                pass
            if proj_name == "dayhoff-tools":
                print("Re-installing dayhoff-tools into the active environment…")
                reinstall_cmd = ["uv", "pip", "install", "-e", ".[full]"]
                print(f"Running command: {BLUE}{' '.join(reinstall_cmd)}{RESET}")
                subprocess.run(reinstall_cmd, check=True)
                print("dayhoff-tools reinstalled in the current environment.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to reinstall dayhoff-tools locally: {e}")

    except FileNotFoundError:
        print(f"Error: {pyproject_path} not found.")
        # No version change happened, so no rollback needed
    except subprocess.CalledProcessError as e:
        print(f"Error during build/upload: {e}")
        # Attempt to roll back version change only if it was bumped successfully
        if current_version and new_version:
            try:
                print(
                    f"Attempting to revert version in {pyproject_path} back to {current_version}..."
                )
                with open(pyproject_path, "r") as f:
                    content_revert = f.read()
                # Use new_version in pattern for reverting
                pattern_revert = re.compile(
                    f'^version\s*=\s*"{re.escape(new_version)}"', re.MULTILINE
                )
                reverted_content, num_revert = pattern_revert.subn(
                    f'version = "{current_version}"', content_revert
                )
                if num_revert > 0:
                    with open(pyproject_path, "w") as f:
                        f.write(reverted_content)
                    print(f"Successfully reverted version in {pyproject_path}.")
                else:
                    print(
                        f"Warning: Could not find version {new_version} to revert in {pyproject_path}."
                    )

                # Also revert mac manifest if we updated it
                try:
                    mac_path = Path(mac_manifest_path)
                    if mac_path.exists():
                        mac_content_revert = mac_path.read_text()
                        mac_reverted, mac_num = pattern_revert.subn(
                            f'version = "{current_version}"', mac_content_revert
                        )
                        if mac_num > 0:
                            mac_path.write_text(mac_reverted)
                            print(
                                f"Successfully reverted version in {mac_manifest_path}."
                            )
                except Exception as e2:
                    print(
                        f"Warning: Failed to revert version change in {mac_manifest_path}: {e2}"
                    )
            except Exception as revert_e:
                print(
                    f"Warning: Failed to revert version change in {pyproject_path}: {revert_e}"
                )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Also attempt rollback here if version was bumped
        if current_version and "new_version" in locals() and new_version:
            try:
                print(
                    f"Attempting to revert version in {pyproject_path} back to {current_version} due to unexpected error..."
                )
                # (Same revert logic as above)
                with open(pyproject_path, "r") as f:
                    content_revert = f.read()
                pattern_revert = re.compile(
                    f'^version\s*=\s*"{re.escape(new_version)}"', re.MULTILINE
                )
                reverted_content, num_revert = pattern_revert.subn(
                    f'version = "{current_version}"', content_revert
                )
                if num_revert > 0:
                    with open(pyproject_path, "w") as f:
                        f.write(reverted_content)
                    print(f"Successfully reverted version in {pyproject_path}.")
                else:
                    print(
                        f"Warning: Could not find version {new_version} to revert in {pyproject_path}."
                    )
                # Also revert mac manifest if necessary
                try:
                    mac_path = Path(mac_manifest_path)
                    if mac_path.exists():
                        mac_content_revert = mac_path.read_text()
                        mac_reverted, mac_num = pattern_revert.subn(
                            f'version = "{current_version}"', mac_content_revert
                        )
                        if mac_num > 0:
                            mac_path.write_text(mac_reverted)
                            print(
                                f"Successfully reverted version in {mac_manifest_path}."
                            )
                except Exception as e2:
                    print(
                        f"Warning: Failed to revert version change in {mac_manifest_path}: {e2}"
                    )
            except Exception as revert_e:
                print(
                    f"Warning: Failed to revert version change in {pyproject_path}: {revert_e}"
                )


# --- Dependency Management Commands ---


def install_dependencies(
    install_project: bool = typer.Option(
        False,
        "--install-project",
        "-p",
        help="Install the local project package itself (with 'full' extras) into the environment.",
    ),
):
    """Install dependencies respecting Mac devcontainer flow and the active venv.

    Behavior:
    - If running on Mac devcontainer (STUDIO_PLATFORM=mac) and `pyproject.mac.toml` exists:
      * Ensure `.mac_uv_project/pyproject.toml` is a copy of `pyproject.mac.toml`
      * Run `uv lock` and `uv sync` in `.mac_uv_project` and always target the active venv with `--active`
      * If `install_project` is true, install the project from repo root into the active env (editable, [full])
    - Otherwise (default path):
      * Operate in repo root, ensure lock, and `uv sync --active` so we don't create `.venv` accidentally
      * If `install_project` is true, sync without `--no-install-project` (installs project)
    """
    # ANSI color codes
    BLUE = "\033[94m"
    RESET = "\033[0m"

    try:
        is_mac = os.environ.get("STUDIO_PLATFORM") == "mac"
        mac_manifest = Path("pyproject.mac.toml")
        if is_mac and mac_manifest.exists():
            # Mac devcontainer flow
            mac_uv_dir = Path(".mac_uv_project")
            mac_uv_dir.mkdir(parents=True, exist_ok=True)
            mac_pyproject = mac_uv_dir / "pyproject.toml"
            mac_pyproject.write_text(mac_manifest.read_text())

            # Ensure lock matches manifest (in mac temp dir)
            print("Ensuring lock file matches pyproject.mac.toml (Mac devcon)…")
            lock_cmd = ["uv", "lock"]
            print(f"Running command: {BLUE}{' '.join(lock_cmd)}{RESET}")
            subprocess.run(lock_cmd, check=True, capture_output=True, cwd=str(mac_uv_dir))

            # Sync into the active environment
            if install_project:
                print("Syncing dependencies into ACTIVE env and installing project [full]…")
                sync_cmd = ["uv", "sync", "--all-groups", "--active"]
                print(f"Running command: {BLUE}{' '.join(sync_cmd)}{RESET}")
                subprocess.run(sync_cmd, check=True, cwd=str(mac_uv_dir))
                # Install project from repo root
                pip_install_cmd = ["uv", "pip", "install", "-e", ".[full]"]
                print(f"Running command: {BLUE}{' '.join(pip_install_cmd)}{RESET}")
                subprocess.run(pip_install_cmd, check=True)
                print("Project installed with 'full' extras successfully.")
            else:
                print("Syncing dependencies into ACTIVE env (project not installed)…")
                sync_cmd = ["uv", "sync", "--all-groups", "--no-install-project", "--active"]
                print(f"Running command: {BLUE}{' '.join(sync_cmd)}{RESET}")
                subprocess.run(sync_cmd, check=True, cwd=str(mac_uv_dir))
                print("Dependencies synced successfully (project not installed).")
        else:
            # Default behavior in repo root, but ensure we target the active env
            print("Ensuring lock file matches pyproject.toml…")
            lock_cmd = ["uv", "lock"]
            print(f"Running command: {BLUE}{' '.join(lock_cmd)}{RESET}")
            subprocess.run(lock_cmd, check=True, capture_output=True)

            if install_project:
                print("Syncing dependencies into ACTIVE env (installing project)…")
                sync_cmd = ["uv", "sync", "--all-groups", "--active"]
                print(f"Running command: {BLUE}{' '.join(sync_cmd)}{RESET}")
                subprocess.run(sync_cmd, check=True)
            else:
                print("Syncing dependencies into ACTIVE env (project not installed)…")
                sync_cmd = ["uv", "sync", "--all-groups", "--no-install-project", "--active"]
                print(f"Running command: {BLUE}{' '.join(sync_cmd)}{RESET}")
                subprocess.run(sync_cmd, check=True)
                print("Dependencies synced successfully (project not installed).")

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode() if e.stderr else "No stderr output."
        print(f"Error occurred during dependency installation/sync: {e}")
        print(f"Stderr: {stderr_output}")
        if "NoSolution" in stderr_output:
            print(
                "\nHint: Could not find a compatible set of dependencies. Check constraints in pyproject.toml."
            )
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Is uv installed and in PATH?")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def update_dependencies(
    update_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Update all dependencies instead of just dayhoff-tools.",
    ),
):
    """Update dependencies to newer versions (Mac-aware, active venv friendly).

    - Default Action (no flags): Updates only 'dayhoff-tools' package to latest,
      updates the manifest's version constraint, and syncs.
    - Flags:
      --all/-a: Updates all dependencies (uv lock --upgrade) and syncs.

    Mac devcontainer behavior:
    - If STUDIO_PLATFORM=mac and `pyproject.mac.toml` exists, operate in `.mac_uv_project/`:
      copy `pyproject.mac.toml` to `.mac_uv_project/pyproject.toml`, run uv there, and always
      use `--active` for sync so installs target the active venv.
    - Update the constraint inside `pyproject.mac.toml`. If not found, try `pyproject.toml`.
    Otherwise (non-Mac), operate in repo root and also target the active venv during sync.
    """
    # ANSI color codes
    BLUE = "\033[94m"
    RESET = "\033[0m"

    is_mac = os.environ.get("STUDIO_PLATFORM") == "mac"
    mac_manifest = Path("pyproject.mac.toml")
    mac_uv_dir = Path(".mac_uv_project")
    lock_file_path = Path("uv.lock")
    pyproject_path = Path("pyproject.toml")

    # Determine action based on flags
    lock_cmd = ["uv", "lock"]
    action_description = ""
    run_pyproject_update = False

    if update_all:
        lock_cmd.append("--upgrade")
        action_description = (
            "Updating lock file for all dependencies to latest versions..."
        )
    else:  # Default behavior: update dayhoff-tools
        lock_cmd.extend(["--upgrade-package", "dayhoff-tools"])
        action_description = (
            "Updating dayhoff-tools lock and pyproject.toml (default behavior)..."
        )
        run_pyproject_update = (
            True  # Only update pyproject if we are doing the dayhoff update
        )

    try:
        # Choose working directory for uv operations
        uv_cwd = None
        manifest_path_for_constraint = pyproject_path
        if is_mac and mac_manifest.exists():
            mac_uv_dir.mkdir(parents=True, exist_ok=True)
            (mac_uv_dir / "pyproject.toml").write_text(mac_manifest.read_text())
            uv_cwd = str(mac_uv_dir)
            lock_file_path = mac_uv_dir / "uv.lock"
            manifest_path_for_constraint = mac_manifest
        # Step 1: Run the update lock command
        print(action_description)
        print(f"Running command: {BLUE}{' '.join(lock_cmd)}{RESET}")
        subprocess.run(lock_cmd, check=True, capture_output=True, cwd=uv_cwd)

        # Step 2: Update pyproject.toml only if doing the dayhoff update (default)
        if run_pyproject_update:
            print(f"Reading {lock_file_path} to find new dayhoff-tools version...")
            if not lock_file_path.exists():
                print(f"Error: {lock_file_path} not found after lock command.")
                return
            locked_version = None
            try:
                lock_data = toml.load(lock_file_path)
                for package in lock_data.get("package", []):
                    if package.get("name") == "dayhoff-tools":
                        locked_version = package.get("version")
                        break
            except toml.TomlDecodeError as e:
                print(f"Error parsing {lock_file_path}: {e}")
                return
            except Exception as e:
                print(f"Error reading lock file: {e}")
                return

            if not locked_version:
                print(
                    f"Error: Could not find dayhoff-tools version in {lock_file_path}."
                )
                return

            print(f"Found dayhoff-tools version {locked_version} in lock file.")
            print(f"Updating {manifest_path_for_constraint} version constraint...")
            try:
                content = manifest_path_for_constraint.read_text()

                package_name = "dayhoff-tools"
                package_name_esc = re.escape(package_name)

                # Regex to match the dependency line, with optional extras and version spec
                pattern = re.compile(
                    rf"^(\s*['\"]){package_name_esc}(\[[^]]+\])?(?:[><=~^][^'\"]*)?(['\"].*)$",
                    re.MULTILINE,
                )

                new_constraint_text = f">={locked_version}"

                def _repl(match: re.Match):
                    prefix = match.group(1)
                    extras = match.group(2) or ""
                    suffix = match.group(3)
                    return (
                        f"{prefix}{package_name}{extras}{new_constraint_text}{suffix}"
                    )

                new_content, num_replacements = pattern.subn(_repl, content)
                if num_replacements > 0:
                    manifest_path_for_constraint.write_text(new_content)
                    print(
                        f"Updated dayhoff-tools constraint in {manifest_path_for_constraint} to '{new_constraint_text}'"
                    )
                else:
                    # Fallback: try the root pyproject if we were targeting mac manifest
                    if manifest_path_for_constraint != pyproject_path and pyproject_path.exists():
                        content2 = pyproject_path.read_text()
                        new_content2, n2 = pattern.subn(_repl, content2)
                        if n2 > 0:
                            pyproject_path.write_text(new_content2)
                            print(
                                f"Updated dayhoff-tools constraint in {pyproject_path} to '{new_constraint_text}'"
                            )
                        else:
                            print(
                                f"Warning: Could not find dayhoff-tools dependency line in {manifest_path_for_constraint} or {pyproject_path} to update constraint."
                            )
                    else:
                        print(
                            f"Warning: Could not find dayhoff-tools dependency line in {manifest_path_for_constraint} to update constraint."
                        )
            except FileNotFoundError:
                print(f"Error: {manifest_path_for_constraint} not found.")
                return
            except Exception as e:
                print(f"Error updating {manifest_path_for_constraint}: {e}")
                print("Proceeding with sync despite pyproject.toml update error.")

        # Step 3: Sync environment
        print("Syncing environment with updated lock file...")
        # Always use --no-install-project for updates
        sync_cmd = ["uv", "sync", "--all-groups", "--no-install-project", "--active"]
        print(f"Running command: {BLUE}{' '.join(sync_cmd)}{RESET}")
        subprocess.run(sync_cmd, check=True, cwd=uv_cwd)

        # Final status message
        if update_all:
            print("All dependencies updated and environment synced successfully.")
        else:  # Default case (dayhoff update)
            print(
                "dayhoff-tools updated, pyproject.toml modified, and environment synced successfully."
            )

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode() if e.stderr else "No stderr output."
        print(f"Error occurred during dependency update/sync: {e}")
        print(f"Stderr: {stderr_output}")
        if "NoSolution" in stderr_output:
            print(
                "\nHint: Could not find a compatible set of dependencies. Check constraints in pyproject.toml."
            )
        elif "unrecognized arguments: --upgrade" in stderr_output:
            print(
                "\nHint: Your version of 'uv' might be too old to support '--upgrade'. Try updating uv."
            )
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Is uv installed and in PATH?")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
