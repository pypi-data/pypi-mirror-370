#!/bin/bash
set -e

echo "=== Running arm-cli system setup ==="
sudo arm-cli system setup --force

echo "=== Running post-setup checks ==="
./tests/integration/check.sh
