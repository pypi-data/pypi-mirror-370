# -- build

FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS build

ARG SETUPTOOLS_SCM_PRETEND_VERSION

WORKDIR /code

COPY .git .git
COPY . ./

# Generate a wheel
RUN if [ -n "$SETUPTOOLS_SCM_PRETEND_VERSION" ]; then \
      export SETUPTOOLS_SCM_PRETEND_VERSION="$SETUPTOOLS_SCM_PRETEND_VERSION"; \
    fi \
    && uv build --wheel

# -- install

FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS install

ENV VIRTUAL_ENV=/opt/igwn-robot-auth

WORKDIR /code

# Generate the virtual environment
RUN uv venv ${VIRTUAL_ENV}

# Install the requirements
COPY pyproject.toml .
RUN uv pip install -r pyproject.toml

# Install the app
COPY --from=build /code/dist/*.whl /code
RUN WHEEL=$(ls /code/*.whl) \
    && uv pip install $WHEEL[kerberos] coloredlogs

# -- application stage

FROM python:3.13-slim AS app

LABEL org.opencontainers.image.license="GPL-3.0-or-later"
LABEL org.opencontainers.image.title="IGWN Robot Auth - Python 3.13 (Debian)"
LABEL org.opencontainers.image.description="IGWN Robot Authorisation tool"
LABEL org.opencontainers.image.source="https://git.ligo.org/computing/software/igwn-robot-auth"
LABEL org.opencontainers.image.vendor="IGWN"
LABEL org.opencontainers.image.authors="Duncan Macleod <duncan.macleod@ligo.org>"
LABEL org.igwn.support="Best effort"

ENV VIRTUAL_ENV=/opt/igwn-robot-auth
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Install libkrb5
RUN apt-get update -yqq \
    && apt-get install -yqq libkrb5-dev \
    && rm -rf /var/lib/apt/lists/*

# Install virtual environment
COPY --from=install ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Create application user
RUN apt-get update -yqq \
    && apt-get install -yqq adduser \
    && addgroup --system igwnrobot \
    && adduser \
      --system \
      --ingroup igwnrobot \
      --home /var/lib/igwnrobot \
      igwnrobot \
    && rm -rf /var/lib/apt/lists/*

# Set default variables for token sharing
ENV XDG_CACHE_HOME=/tmp
ENV XDG_RUNTIME_DIR=/tokens
RUN mkdir -p /tokens && chmod 1777 /tokens

# Run the igwn-robot-get script as the igwnrobot user by default
USER igwnrobot
ENTRYPOINT ["/opt/igwn-robot-auth/bin/igwn-robot-get"]
