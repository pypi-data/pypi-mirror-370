#!/bin/bash
set -e

# TODO Rethink the X11 access in the integration tests.
if [[ -z "$CI" ]]; then
  echo "==> Allowing X11 access..."
  xhost +local:docker || true
fi

echo "==> Building integration Docker image..."
docker build -t arm-cli-integration -f ./tests/integration/Dockerfile .

echo "==> Running integration tests..."

if [[ -z "$CI" ]]; then
  docker run --rm -it \
    --privileged \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /var/run/docker.sock:/var/run/docker.sock \
    arm-cli-integration
else
  docker run --rm \
    --privileged \
    -v /var/run/docker.sock:/var/run/docker.sock \
    arm-cli-integration
fi
