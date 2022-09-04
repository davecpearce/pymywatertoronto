# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.2/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Configure apt and install packages
RUN apt-get update && apt-get -y dist-upgrade \
    && apt-get -y install --no-install-recommends apt-utils dialog 2>&1 \
    #
    # Verify git, process tools, lsb-release (common in install instructions for CLIs) installed
    && apt-get -y install git \
    sudo \
    #
    # Install flake8
    && pip --disable-pip-version-check --no-cache-dir install flake8 \
    #
    # Install pre-commit
    && pip --disable-pip-version-check --no-cache-dir install pre-commit \
    #
    # Install bumpver
    && pip --disable-pip-version-check --no-cache-dir install bumpver \
    #
    # Install build
    && pip --disable-pip-version-check --no-cache-dir install build \
    #
    # Install twine
    #
    && pip --disable-pip-version-check --no-cache-dir install twine \
    #
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
