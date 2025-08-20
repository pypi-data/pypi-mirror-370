
# Setup autocomplete
eval "$(_ARM_CLI_COMPLETE=zsh_source arm-cli)"

# Export for use when launching Docker to match host file ownership
export CURRENT_UID=$(id -u):$(id -g)

# Allow Docker containers to access X11 for GUI apps
if command -v xhost >/dev/null 2>&1; then
    xhost +local:docker > /dev/null 2>&1
fi 