#!/bin/bash
set -e
# TODO: Make this more comprehensive. This is a proof of concept check
echo "[✓] Checking data directories setup..."

# Define the expected data directories
data_dirs=("/DATA/influxdb2" "/DATA/images" "/DATA/node_exporter")

# Get current user UID and GID
current_uid=$(id -u)
current_gid=$(id -g)

echo "Current user: $(id -un) (UID: $current_uid, GID: $current_gid)"

# Check each directory
for directory in "${data_dirs[@]}"; do
    echo "Checking directory: $directory"
    
    # Check if directory exists
    if [ ! -d "$directory" ]; then
        echo "❌ Directory $directory does not exist"
        exit 1
    fi
    
    # Check ownership
    dir_uid=$(stat -c '%u' "$directory")
    dir_gid=$(stat -c '%g' "$directory")
    
    if [ "$dir_uid" != "$current_uid" ] || [ "$dir_gid" != "$current_gid" ]; then
        echo "❌ Directory $directory has wrong ownership: UID=$dir_uid, GID=$dir_gid (expected: UID=$current_uid, GID=$current_gid)"
        exit 1
    fi
    
    # Check permissions (should be 775)
    dir_perms=$(stat -c '%a' "$directory")
    if [ "$dir_perms" != "775" ]; then
        echo "❌ Directory $directory has wrong permissions: $dir_perms (expected: 775)"
        exit 1
    fi
    
    echo "✓ Directory $directory is properly configured"
done

echo "[✓] All data directories are set up correctly!"
