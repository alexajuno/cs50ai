# Development stage
FROM ubuntu:22.04 AS development

# Prevent timezone prompt
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and development dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    python3-venv \
    git \
    openssh-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -m -s /bin/bash appuser
RUN mkdir -p /app/.submit50 && \
    chown -R appuser:appuser /app /opt/venv

# Create submit50 config directory
RUN mkdir -p /home/appuser/.config/submit50
RUN chown -R appuser:appuser /home/appuser/.config

# Switch to appuser for configuration
USER appuser

# Set up git configuration
RUN git config --global credential.helper store

# Create script to setup credentials
COPY --chown=appuser:appuser scripts/setup-credentials.sh /home/appuser/setup-credentials.sh
RUN chmod +x /home/appuser/setup-credentials.sh

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app

# Copy virtual environment from development stage
COPY --from=development /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user
RUN useradd -m -s /bin/bash appuser

# Copy only necessary files
COPY degrees/degrees.py degrees/
COPY degrees/util.py degrees/
COPY requirements.txt .

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser