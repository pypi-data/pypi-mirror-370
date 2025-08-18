# ctenv

[![GitHub repo](https://img.shields.io/badge/github-repo-green)](https://github.com/osks/ctenv)
[![PyPI](https://img.shields.io/pypi/v/ctenv.svg)](https://pypi.org/project/ctenv/)
[![Changelog](https://img.shields.io/github/v/release/osks/ctenv?include_prereleases&label=changelog)](https://github.com/osks/ctenv/releases)
[![Tests](https://github.com/osks/ctenv/actions/workflows/test.yml/badge.svg)](https://github.com/osks/ctenv/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/osks/ctenv/blob/master/LICENSE)

Container environment as current user, in any image, preserving user identity.

Start container based on any image, with current directory mounted and
runs as your own user in the container. Run a command or start an
interactive shell.


## Install

```bash
# Install with pip
$ pip install ctenv

# Install with uv
$ uv tool install ctenv

# Or run directly without installing
$ uv tool run ctenv --help
```

Recommend [installing uv](https://docs.astral.sh/uv/getting-started/installation/).


## Usage

```bash
# Interactive shell in ubuntu container
$ ctenv run --image ubuntu -- bash

# Run a configured container
$ ctenv run my-node

# Run a custom command and mount a volume
$ ctenv run my-node --volume ./tests -- npm test
```

## Why ctenv?

When running containers with mounted directories, files created inside often have root ownership or wrong permissions. ctenv solves this by:

- Creating a matching user (same UID/GID) dynamically in existing images at runtime
- Mounting your current directory with correct permissions
- Using [`gosu`](https://github.com/tianon/gosu) to drop privileges after container setup

This works with any existing Docker image without modification - no
custom Dockerfiles needed. Provides similar functionality to Podman's
`--userns=keep-id` but works with Docker. Also similar to Development
Containers but focused on running individual commands rather than
persistent development environments.

Under the hood, ctenv starts containers as root for file ownership
setup, then drops privileges using bundled `gosu` binaries before
executing your command. It generates bash entrypoint scripts
dynamically to handle user creation and environment setup.

## Highlights

- Works with existing images without modifications
- Files created have your UID/GID (preserves permissions)
- Convenient volume mounting like `-v ~/.gitconfig` (mounts to same path in container)
- Simple configuration with reusable `.ctenv.toml` setups

## Requirements

- Python 3.10+
- Docker (tested on Linux/macOS)

## Features

- User identity preservation (matching UID/GID in container)
- Volume mounting with shortcuts like `-v ~/.gitconfig` (mounts to same path)
- Volume ownership fixing with custom `:chown` option (similar to Podman's `:U` and `:chown`)
- Post-start commands for running setup as root before dropping to user permissions
- Template variables with environment variables, like `${env.HOME}`
- Configuration file support with reusable container definitions
- Cross-platform support for linux/amd64 and linux/arm64 containers
- Bundled gosu binaries for privilege dropping
- Interactive and non-interactive command execution

## Configuration

ctenv supports having a `.ctenv.toml` either in HOME or in project
directores. When located in a project, it will use the path to the
config file as project root.

Create `.ctenv.toml` for reusable container setups:

```toml
[defaults]
command = "zsh" # Run a shell for interactive use

[containers.python]
image = "python:3.11"
env = [
    "MY_API_KEY", # passed from environment when run
    "ENV=dev",
]
volumes = ["~/.cache/pip"]

```

Then run:
```bash
$ ctenv run python -- python script.py
```

## Common Use Cases

### Build Systems
Use containerized build environments:
```toml
[containers.build-system]
image = "some-build-system:v17"
volumes = ["build-cache:/var/cache:rw,chown"]
```

### Development Tools
Run linters, formatters, or compilers from containers:
```bash
$ ctenv run --image rust:latest -- cargo fmt
$ ctenv run --image my-node-env -- eslint src/
```

### Claude Code
Run Claude Code in a container for isolation with configuration for convenient usage:

`~/.ctenv.toml`:
```
# Run Claude Code in container
[containers.claude]
volumes = ["~/.claude.json", "~/.claude/"]
command = "claude" # Run claude directly

# Builds an image so you don't have to reinstall every time
[containers.claude.build]
dockerfile_content = """
FROM node:20
RUN npm install -g @anthropic-ai/claude-code
"""
```

Then start with: `ctenv run claude`


## Detailed Examples

### Claude Code

Basic example:

```shell
$ ctenv run --image node:20 -v ~/.claude.json -v ~/.claude/ --post-start-command "npm install -g @anthropic-ai/claude-code" -- claude
```

That would install it every time you run it. To avoid that, we can use
ctenv to build an image with Claude Code:

```shell
$ ctenv run --build-dockerfile-content "FROM node:20\nRUN npm install -g @anthropic-ai/claude-code" -v ~/.claude.json -v ~/.claude/ -- claude
```

You likely want to configure this for conveniency:
```
# Run Claude Code in container
[containers.claude]
volumes = ["~/.claude.json", "~/.claude/"]
command = "claude" # Run claude directly

# Builds an image so you don't have to reinstall every time
[containers.claude.build]
dockerfile_content = """
FROM node:20
RUN npm install -g @anthropic-ai/claude-code
"""
```

If you have an existing image with a build environment already, use that and install Claude Code:
```toml
[containers.claude]
volumes = ["~/.claude.json", "~/.claude/"]
command = "claude"

[containers.claude.build]
dockerfile_content = """
FROM my-build-env:latest
RUN npm install -g @anthropic-ai/claude-code
"""
```
and run with: `ctenv run claude`

ctenv by default mounts the current directory as "workspace" and
switches to it, so it would start Claude Code in with the current
directory mounted in the container.

If you don't already have an image with your development tools in
(`node:20` doesn't include that much), you likely want to write a
`Dockerfile` and install more tools in it for Claude and you to use.
```
[containers.claude.build]
dockerfile = "Dockerfile" # instead of dockerfile_content
```

Can for example also use iptables to restrict network access:
```toml
[containers.claude]
# ...
network = "bridge"
run_args = ["--cap-add=NET_ADMIN"]
post_start_commands = [
    "iptables -A OUTPUT -d 192.168.0.0/24 -j DROP",
]
```

Note: On macOS, Claude Code stores credentials in the keychain by default. When run in a container, it will create `~/.claude/.credentials.json` instead, which persists outside the container due to the volume mount.

Note: There are also other tools for running Claude Code in a container, such as devcontainers: https://docs.anthropic.com/en/docs/claude-code/devcontainer



### Build System with Caching
Complex build environment with shared caches:

```toml
[containers.build]
image = "registry.company.internal/build-system:v1"
env = [
    "BB_NUMBER_THREADS",
    "CACHE_MIRROR=http://build-cache.company.internal/",
    "BUILD_CACHES_DIR=/var/cache/build-caches/image-${image|slug}",
]
volumes = [
    "build-caches-user-${env.USER}:/var/cache/build-caches:rw,chown",
    "${env.HOME}/.ssh:/home/builduser/.ssh:ro"
]
post_start_commands = ["source /venv/bin/activate"]
```

This setup ensures the build environment matches the user's environment while sharing caches between different repository clones.


## History

The background for ctenv was a bash script that I developed at work
([Agama](https://www.agama.tv/)) for running our build system in a
container. Besides running the build, it was useful to also be able to
run and use the compiled code in the build system environment, which
had older libraries than the modern OSes that was used by the
developers.

ctenv is a much more generic tool than that bash script and without
the many hard-coded parts. Written in Python and support for config
files and much more.
