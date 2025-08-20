import subprocess

import click
import docker
import inquirer

from arm_cli.settings import get_setting


@click.group()
def container():
    """Basic tools for managing Docker containers. For more extensive tooling,
    try lazydocker (brew install jesseduffield/lazydocker/lazydocker)"""
    pass


def get_running_containers():
    """Retrieve a list of running Docker containers"""
    client = docker.from_env()
    return client.containers.list(filters={"status": "running"})


@container.command("list")
@click.pass_context
def list_containers(ctx):
    """List all Docker containers"""
    config = ctx.obj["config"]  # noqa: F841 - config available for future use
    containers = get_running_containers()

    if containers:
        for container in containers:
            print(f"{container.id[:12]}: {container.name}")
    else:
        print("No running containers found.")


@container.command("attach")
@click.pass_context
def attach_container(ctx):
    """Interactively select a running Docker container and attach to it"""
    config = ctx.obj["config"]  # noqa: F841 - config available for future use
    containers = get_running_containers()

    if not containers:
        print("No running containers found.")
        return

    container_choices = [
        inquirer.List(
            "container",
            message="Select a container to attach to",
            choices=[f"{container.name} ({container.id[:12]})" for container in containers],
            carousel=True,
        )
    ]

    answers = inquirer.prompt(container_choices)
    if not answers:
        print("No container selected.")
        return

    selected_container_name = answers["container"].split(" ")[0]  # Extract name

    print(f"Attaching to {selected_container_name}...")

    cmd = """
    if [ -f /ros_entrypoint.sh ]; then
        source /ros_entrypoint.sh
    fi
    if [ -f /interactive_entrypoint.sh ]; then
        source /interactive_entrypoint.sh
    fi
    exec bash
    """

    try:
        subprocess.run(
            ["docker", "exec", "-it", selected_container_name, "bash", "-c", cmd], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error attaching to container: {e}")
    except KeyboardInterrupt:
        print("\nExiting interactive session...")


@container.command("restart")
@click.pass_context
def restart_container(ctx):
    """Interactively select a running Docker container and restart it"""
    config = ctx.obj["config"]  # noqa: F841 - config available for future use
    containers = get_running_containers()

    if not containers:
        print("No running containers found.")
        return

    container_choices = [
        inquirer.List(
            "container",
            message="Select a container to restart",
            choices=[f"{container.name} ({container.id[:12]})" for container in containers],
            carousel=True,
        )
    ]

    answers = inquirer.prompt(container_choices)
    if not answers:
        print("No container selected.")
        return

    selected_container_name = answers["container"].split(" ")[0]

    print(f"Restarting {selected_container_name}...")

    try:
        client = docker.from_env()
        container = client.containers.get(selected_container_name)
        container.restart()
        print(f"Container {selected_container_name} restarted successfully.")
    except docker.errors.NotFound:
        print(f"Error: Container {selected_container_name} not found.")
    except docker.errors.APIError as e:
        print(f"Error restarting container: {e}")


@container.command("stop")
@click.pass_context
def stop_container(ctx):
    """Interactively select a running Docker container and stop it"""
    config = ctx.obj["config"]  # noqa: F841 - config available for future use
    containers = get_running_containers()

    if not containers:
        print("No running containers found.")
        return

    container_choices = [
        inquirer.List(
            "container",
            message="Select a container to stop",
            choices=[f"{container.name} ({container.id[:12]})" for container in containers],
            carousel=True,
        )
    ]

    answers = inquirer.prompt(container_choices)
    if not answers:
        print("No container selected.")
        return

    selected_container_name = answers["container"].split(" ")[0]  # Extract name

    print(f"Stopping {selected_container_name}...")

    try:
        client = docker.from_env()
        container = client.containers.get(selected_container_name)
        container.stop()
        print(f"Container {selected_container_name} stopped successfully.")
    except docker.errors.NotFound:
        print(f"Error: Container {selected_container_name} not found.")
    except docker.errors.APIError as e:
        print(f"Error stopping container: {e}")
