
# Setup autocomplete
_ARM_CLI_COMPLETE=fish_source arm-cli | source

# Export for use when launching Docker to match host file ownership
set -x CURRENT_UID (id -u):(id -g)

# Allow Docker containers to access X11 for GUI apps
if type -q xhost
    xhost +local:docker > /dev/null 2>&1
end