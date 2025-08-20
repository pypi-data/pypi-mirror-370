FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    sudo python3 python3-pip docker.io \
    x11-apps xauth x11-utils && \
    rm -rf /var/lib/apt/lists/*

# Create test user with passwordless sudo
RUN useradd -m testuser && echo "testuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create docker group with GID 998 (host docker group GID)
# TODO: We shouldn't be creating the docker group here. The creation of that group is what we're testing.
RUN groupdel docker || true && groupadd -g 998 docker && usermod -aG docker testuser

# Switch to testuser for the rest of the setup
USER testuser
WORKDIR /home/testuser

# Copy project code
COPY --chown=testuser:testuser . /home/testuser/arm-cli
WORKDIR /home/testuser/arm-cli

# Upgrade pip, setuptools, wheel, setuptools_scm then install arm-cli in editable mode
RUN sudo pip3 install --upgrade pip setuptools>=65.5.0 wheel setuptools_scm && \
    sudo pip3 install -e .

# Make scripts executable
RUN chmod +x ./tests/integration/run.sh ./tests/integration/check.sh

ENTRYPOINT ["./tests/integration/run.sh"]
