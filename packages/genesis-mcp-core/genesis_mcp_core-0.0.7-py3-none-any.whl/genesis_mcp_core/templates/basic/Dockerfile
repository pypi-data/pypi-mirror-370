# Build stage - Use Ubuntu 24.04 for better security
FROM ubuntu:24.04 AS builder

LABEL name="{{ project_name }}"
LABEL description="{{ project_name | title }} - MCP Server built with Genesis MCP Core SDK"
LABEL version="1.0.0"

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    cargo \
    rustc \
    git \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./
COPY README.md LICENSE* ./
COPY {{ project_name_normalized }}/ ./{{ project_name_normalized }}/
COPY connectors/ ./connectors/

# Create virtual environment and install dependencies
RUN python3.12 -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --frozen --no-cache --no-dev

# Production stage - Use minimal Ubuntu
FROM ubuntu:24.04

# Install only runtime dependencies with minimal packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.12 \
    libpq5 \
    curl \
    ca-certificates \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r {{ project_name_normalized }} && useradd -r -m -g {{ project_name_normalized }} {{ project_name_normalized }}

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown={{ project_name_normalized }}:{{ project_name_normalized }} /app/.venv /app/.venv

# Copy application files
COPY --chown={{ project_name_normalized }}:{{ project_name_normalized }} LICENSE* ./
COPY --chown={{ project_name_normalized }}:{{ project_name_normalized }} README.md ./
COPY --chown={{ project_name_normalized }}:{{ project_name_normalized }} {{ project_name_normalized }}/ ./{{ project_name_normalized }}/
COPY --chown={{ project_name_normalized }}:{{ project_name_normalized }} main.py ./
COPY --chown={{ project_name_normalized }}:{{ project_name_normalized }} env.example ./
COPY --chown={{ project_name_normalized }}:{{ project_name_normalized }} connectors/ ./connectors/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    HOST=0.0.0.0 \
    PORT={{ SERVER_PORT }} \
    SERVER__HOST=0.0.0.0 \
    SERVER__PORT={{ SERVER_PORT }}

# Create necessary directories
RUN mkdir -p /tmp/{{ project_name_normalized }} /home/{{ project_name_normalized }}/.cache /app/logs /app/data && \
    chown -R {{ project_name_normalized }}:{{ project_name_normalized }} /tmp/{{ project_name_normalized }} /home/{{ project_name_normalized }}/.cache /app/logs /app/data

# Switch to non-root user
USER {{ project_name_normalized }}

# Expose port
EXPOSE {{ SERVER_PORT }}

# Health check - validates service health
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:{{ SERVER_PORT }}/health || exit 1

# Run the application via main.py
CMD ["python", "main.py"]
