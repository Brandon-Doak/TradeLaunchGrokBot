FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Stable system packages. Project Python dependencies are installed later by
# the environment `install` step, against the checked-out source.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# ubuntu:24.04 ships a non-root "ubuntu" user (uid 1000); run as it.
USER ubuntu
