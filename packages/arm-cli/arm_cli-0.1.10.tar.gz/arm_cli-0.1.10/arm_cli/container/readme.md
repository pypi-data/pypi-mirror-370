Container Compliance for arm-cli

While not strictly necessary, to work with arm-cli's interactive attach:

## Entrypoint Scripts

arm-cli attach will automatically source the following scripts if they exist:

1. `/ros_entrypoint.sh` - Standard ROS entrypoint script
2. `/interactive_entrypoint.sh` - Custom interactive entrypoint script

### ROS Entrypoint Script

Most ROS containers already include `/ros_entrypoint.sh`. This script typically:
- Sets up ROS environment variables
- Sources ROS setup files
- Configures the ROS workspace

### Interactive Entrypoint Script

Add /interactive_entrypoint.sh in your image:

```
#!/bin/bash
[ -f /opt/ros/$ROS_DISTRO/setup.bash ] && source /opt/ros/$ROS_DISTRO/setup.bash
[ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash
exec "$@"
```

Dockerfile:
```
COPY interactive_entrypoint.sh /interactive_entrypoint.sh
ENTRYPOINT ["/interactive_entrypoint.sh"]
```

Behavior:
arm-cli attach <container> sources both scripts in order if present:
1. First sources `/ros_entrypoint.sh` (if it exists)
2. Then sources `/interactive_entrypoint.sh` (if it exists)
3. Falls back to plain bash if neither exists