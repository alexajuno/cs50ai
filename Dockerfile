# Use Ubuntu as base image for better package compatibility
FROM ubuntu:22.04

# Prevent timezone prompt during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and common development dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    git \
    openssh-client \
    build-essential \
    # Dependencies commonly needed for packages like pygame
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create and activate virtual environment
RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user
RUN useradd -m -s /bin/bash appuser

# Create necessary directories
RUN mkdir -p /home/appuser/.config/submit50 && \
    mkdir -p /app/.submit50 && \
    chown -R appuser:appuser /app /opt/venv /home/appuser

# Switch to non-root user
USER appuser

# Set up git configuration
RUN git config --global credential.helper store

# Copy and setup the credentials script
COPY --chown=appuser:appuser scripts/setup-credentials.sh /home/appuser/setup-credentials.sh
RUN chmod +x /home/appuser/setup-credentials.sh

# Default command
CMD ["/bin/bash"]