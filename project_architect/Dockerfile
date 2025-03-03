# Dockerfile for Project Architect
# Multi-stage build to optimize the final image size and security

# ===== STAGE 1: Build dependencies =====
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Set working directory
WORKDIR /app

# Copy requirements from setup.py
COPY setup.py pyproject.toml ./
COPY README.md ./

# Create minimal src directory structure for setup.py to work
RUN mkdir -p src
COPY src/__init__.py src/

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install the package with development dependencies
RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

# ===== STAGE 2: Runtime image =====
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production

# Create a non-privileged user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Create directory for generated projects with appropriate permissions
RUN mkdir -p /app/generated_projects && \
    chown -R appuser:appuser /app/generated_projects

# Create directory for logs with appropriate permissions
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Create volume for generated projects and configuration
VOLUME ["/app/generated_projects", "/app/config"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set default command to run the API server
# Can be overridden with docker run command
CMD ["uvicorn", "src.interfaces.api:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative entry points:
# For CLI usage: docker run -it --rm image_name python -m src.interfaces.cli
# For running tests: docker run -it --rm image_name pytest