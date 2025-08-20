import os
import stat
import subprocess
import sys

import click

from arm_cli.system.shell_scripts import detect_shell, get_current_shell_addins


def get_original_user():
    """Get the original user's identity when running with sudo"""
    # Get the original user from SUDO_USER environment variable
    original_user = os.getenv("SUDO_USER")
    if original_user:
        return original_user

    # Fallback: try to get from who am i
    try:
        result = subprocess.run(["who", "am", "i"], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            return result.stdout.strip().split()[0]
    except (subprocess.CalledProcessError, IndexError):
        pass

    # Final fallback: current user
    return os.getenv("USER") or os.getenv("LOGNAME") or os.getlogin()


def get_original_user_uid_gid():
    """Get the original user's UID and GID when running with sudo"""
    original_user = get_original_user()

    try:
        # Get UID
        uid_result = subprocess.run(
            ["id", "-u", original_user], capture_output=True, text=True, check=True
        )
        uid = int(uid_result.stdout.strip())

        # Get GID
        gid_result = subprocess.run(
            ["id", "-g", original_user], capture_output=True, text=True, check=True
        )
        gid = int(gid_result.stdout.strip())

        return uid, gid
    except (subprocess.CalledProcessError, ValueError):
        # Fallback to current user if we can't get original user info
        return os.getuid(), os.getgid()


def check_xhost_setup():
    """Check if xhost is already configured for Docker"""
    try:
        result = subprocess.run(["xhost"], capture_output=True, text=True, check=True)
        return "LOCAL:docker" in result.stdout
    except subprocess.CalledProcessError:
        return False


def setup_xhost(force=False):
    """Setup xhost for GUI applications"""
    # Skip xhost setup in Docker environment TODO: Handle this better in integration tests and remove this
    if os.path.exists("/.dockerenv"):
        print("Skipping xhost setup in Docker environment.")
        return

    try:
        # Check if xhost is already configured
        if check_xhost_setup():
            print("X11 access for Docker containers is already configured.")
            return

        # Ensure xhost allows local Docker connections
        print("Setting up X11 access for Docker containers...")
        if not force:
            if not click.confirm("Do you want to configure X11 access for Docker containers?"):
                print("X11 setup cancelled.")
                return

        subprocess.run(["xhost", "+local:docker"], check=True)
        print("xhost configured successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error configuring xhost: {e}")


def check_sudo_privileges():
    """Check if the user has sudo privileges"""
    try:
        subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_data_directories_setup(data_directory="/DATA"):
    """Check if data directories are already properly set up"""
    data_dirs = [
        os.path.join(data_directory, "influxdb2"),
        os.path.join(data_directory, "images"),
        os.path.join(data_directory, "node_exporter"),
    ]
    current_uid = os.getuid()
    current_gid = os.getgid()

    for directory in data_dirs:
        # Check if directory exists
        if not os.path.exists(directory):
            return False

        # Check ownership
        try:
            stat_info = os.stat(directory)
            if stat_info.st_uid != current_uid or stat_info.st_gid != current_gid:
                return False

            # Check permissions (should be 775)
            mode = stat_info.st_mode
            if not (mode & stat.S_IRWXU and mode & stat.S_IRWXG and not mode & stat.S_IWOTH):
                return False

        except (OSError, PermissionError):
            return False

    return True


def setup_data_directories(force=False, data_directory="/DATA"):
    """Setup data directories for the ARM system"""
    try:
        # Check if directories are already properly set up
        if check_data_directories_setup(data_directory):
            print("Data directories are already properly set up.")
            return True

        print("Setting up data directories...")

        # Check if user has sudo privileges
        if not check_sudo_privileges():
            print("This operation requires sudo privileges.")
            print("Please run: sudo arm-cli system setup")
            return False

        # Ask user for confirmation
        print("This will create the following directories:")
        data_dirs = [
            os.path.join(data_directory, "influxdb2"),
            os.path.join(data_directory, "images"),
            os.path.join(data_directory, "node_exporter"),
        ]
        for directory in data_dirs:
            print(f"  - {directory}")
        print("And set appropriate ownership and permissions.")

        if not force:
            if not click.confirm("Do you want to proceed?"):
                print("Setup cancelled.")
                return False

        # Get original user UID and GID (works correctly even when running with sudo)
        uid, gid = get_original_user_uid_gid()

        print("Creating directories and setting permissions...")

        # Create all directories in one sudo command
        mkdir_cmd = ["sudo", "mkdir", "-p"] + data_dirs
        subprocess.run(mkdir_cmd, check=True)
        print("Created directories.")

        # Set ownership for all directories in one sudo command
        chown_cmd = ["sudo", "chown", "-R", f"{uid}:{gid}"] + data_dirs
        subprocess.run(chown_cmd, check=True)
        print("Set ownership.")

        # Set permissions for all directories in one sudo command
        chmod_cmd = ["sudo", "chmod", "-R", "775"] + data_dirs
        subprocess.run(chmod_cmd, check=True)
        print("Set permissions.")

        print("Data directories setup completed successfully.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error setting up data directories: {e}")
        print("Please ensure you have sudo privileges.")
        return False
    except Exception as e:
        print(f"Unexpected error during data directory setup: {e}")
        return False


def check_docker_group_setup():
    """Check if the user is already in the docker group"""
    try:
        result = subprocess.run(["id", "-nG"], capture_output=True, text=True, check=True)
        groups = result.stdout.strip().split()
        return "docker" in groups
    except subprocess.CalledProcessError:
        return False


def setup_docker_group(force=False):
    """Add user to docker group (requires sudo)"""
    try:
        # Check if user is already in docker group
        if check_docker_group_setup():
            print("User is already in the docker group.")
            return True

        print("User is not in the docker group.")
        print("This operation requires sudo privileges.")
        print("Please run: arm-cli system setup")

        if not force:
            if not click.confirm("Do you want to add yourself to the docker group now?"):
                print("Docker group setup cancelled.")
                return False

        # Check if user has sudo privileges
        if not check_sudo_privileges():
            print("This operation requires sudo privileges.")
            print("Please run: sudo arm-cli system setup")
            return False

        # Add user to docker group (use original user when running with sudo)
        username = get_original_user()
        subprocess.run(["sudo", "usermod", "-aG", "docker", username], check=True)

        print(f"Added {username} to docker group successfully.")
        print("Please log out and back in for the docker group changes to take effect,")
        print("or run 'newgrp docker' in a new terminal session.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error adding user to docker group: {e}")
        print("Please ensure you have sudo privileges.")
        return False
    except Exception as e:
        print(f"Unexpected error during docker group setup: {e}")
        return False


def is_line_in_file(line, filepath) -> bool:
    """Checks if a line is already in a file"""
    with open(filepath, "r") as f:
        return any(line.strip() in file_line.strip() for file_line in f)


def setup_shell(force=False):
    """Setup shell addins for autocomplete"""
    shell = detect_shell()

    if "bash" in shell:
        # Use original user's home directory when running with sudo
        original_user = get_original_user()
        if original_user != os.getenv("USER"):
            # We're running with sudo, use original user's home
            bashrc_path = f"/home/{original_user}/.bashrc"
        else:
            # Normal operation, use current user's home
            bashrc_path = os.path.expanduser("~/.bashrc")

        line = f"source {get_current_shell_addins()}"
        if not is_line_in_file(line, bashrc_path):
            print(f'Adding \n"{line}"\nto {bashrc_path}')
            if not force:
                if not click.confirm("Do you want to add shell autocomplete to ~/.bashrc?"):
                    print("Shell setup cancelled.")
                    return

            with open(bashrc_path, "a") as f:
                f.write(f"\n{line}\n")
        else:
            print("Shell addins are already configured in ~/.bashrc")
    else:
        print(f"Unsupported shell: {shell}", file=sys.stderr)
