# arm-cli

[![PyPI](https://img.shields.io/pypi/v/arm-cli.svg)](https://pypi.org/project/arm-cli/)
[![Changelog](https://img.shields.io/github/v/release/mpowelson/arm-cli?include_prereleases&label=changelog)](https://github.com/mpowelson/arm-cli/releases)
[![Tests](https://github.com/mpowelson/arm-cli/actions/workflows/test.yml/badge.svg)](https://github.com/mpowelson/arm-cli/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mpowelson/arm-cli/blob/master/LICENSE)

Experimental CLI for deploying robotic applications

## Installation

Install this tool using `pip`:
```bash
pip install arm-cli
```

Once installed, setup the CLI initially by running `arm-cli system setup`. You may need to rerun if you update the CLI via pip. This will do things like configure system settings to enable tab complete.

**Note**: If you installed the CLI with `pip install --user`, you may need to manually run the local bin version the first time:
```bash
~/.local/bin/arm-cli system setup
```

## Usage
### Initial Setup 
For help, run:
```bash
arm-cli --help
```
You can also use:

```bash
python -m arm_cli --help
```

### Container Management
The CLI includes tools for managing Docker containers:

```bash
# List running containers
arm-cli container list

# Attach to a container interactively (sources ROS and interactive entrypoints)
arm-cli container attach

# Restart a container
arm-cli container restart

# Stop a container
arm-cli container stop
```

For more details on container compliance, see [arm_cli/container/readme.md](arm_cli/container/readme.md).
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment. From the root of the repo:
```bash
cd arm-cli
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[dev]'
```
To run the tests:
```bash
python -m pytest
```
### Troubleshooting

- If editable install fails, ensure you have a modern toolchain:
  ```bash
  python -m pip install --upgrade pip setuptools wheel build setuptools-scm
  ```
- If the reported version is `0+unknown`, ensure you're working from a Git checkout with tags available:
  ```bash
  git fetch --tags --force
  ```


