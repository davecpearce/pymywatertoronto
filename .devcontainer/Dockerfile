# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.2/containers/python-3/.devcontainer/base.Dockerfile

ARG VARIANT="3.11"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt update

WORKDIR /workspaces/pymywatertoronto
ARG REQUIREMENTS_DEV_FILE='requirements_dev.txt'

COPY requirements.txt ./
COPY ${REQUIREMENTS_DEV_FILE} .
RUN python3 -m pip install -r ${REQUIREMENTS_DEV_FILE}

ENV SHELL /bin/bash
