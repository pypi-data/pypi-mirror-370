#!/usr/bin/env bash

## Setup PATH to include $HOME/.local/bin
setup_path() {
    # Add $HOME/.local/bin to PATH if it's not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

## Setup autocomplete for arm-cli
setup_arm_cli_completion() {
    if command -v arm-cli >/dev/null 2>&1; then
        local completion_script="$HOME/.arm_cli_completion.sh"
        # Generate completion script if it doesn't exist or arm-cli was updated
        if [ ! -f "$completion_script" ] || [ "$(command -v arm-cli)" -nt "$completion_script" ]; then
            _ARM_CLI_COMPLETE=bash_source arm-cli > "$completion_script" 2>/dev/null || true
        fi

        # Source the script or fallback to dynamic completion
        if [ -f "$completion_script" ]; then
            source "$completion_script" 2>/dev/null || true
        else
            eval "$(_ARM_CLI_COMPLETE=bash_source arm-cli 2>/dev/null)" 2>/dev/null || true
        fi
    fi
}

## Setup alias and completion
setup_alias() {
    local alias_name="aa"
    local cli_path
    cli_path=$(command -v arm-cli)

    if [ -n "$cli_path" ]; then
        if [[ $- == *i* ]]; then  # Only define alias in interactive shells
            alias "$alias_name"="$cli_path"
            complete -o default -F _arm_cli_completion "$alias_name" 2>/dev/null || true
            
            # Add cdp alias to change to project directory
            alias cdp='cd "$(arm-cli projects info --field "project_directory" | sed "s|^~|$HOME|")"'
            
            # Add cdc alias to change to code directory
            alias cdc='cd "$(arm-cli self settings get cdc_path | sed "s|^~|$HOME|")"'
        fi
    fi
}

## Set UID for Docker
export CURRENT_UID="$(id -u):$(id -g)"

## Allow Docker containers to access X11
allow_x11_docker_access() {
    if command -v xhost >/dev/null 2>&1 && [ -n "$DISPLAY" ]; then
        xhost +local:docker >/dev/null 2>&1 || true
    fi
}

## Check docker group membership
check_docker_group() {
    if ! id -nG "$USER" | grep -qw docker; then
        echo "Warning: $USER is not in the docker group."
        echo "To add yourself to the docker group, run: arm-cli system setup"
    fi
}

# Run setup steps
setup_path
setup_arm_cli_completion
setup_alias
allow_x11_docker_access
check_docker_group
