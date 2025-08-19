# MAOS Backend API Docker Image
# Multi-stage build for production deployment

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    MAOS_ENV=production \
    LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system --gid 1001 maos \
    && adduser --system --uid 1001 --gid 1001 maos

# Create app directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=maos:maos src/ src/
COPY --chown=maos:maos examples/ examples/
COPY --chown=maos:maos config/ config/

# Create directories for runtime data
RUN mkdir -p /app/data /app/logs && \
    chown -R maos:maos /app/data /app/logs

# Switch to non-root user
USER maos

# Expose port
EXPOSE 8000

# Health check
HEALTHCHEK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "examples/backend_api_example.py", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM production as development

# Switch back to root for development dependencies
USER root

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install additional development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Switch back to maos user
USER maos

# Override environment for development
ENV MAOS_ENV=development \
    LOG_LEVEL=DEBUG

# Development command (with reload)
CMD ["python", "examples/backend_api_example.py", "--host", "0.0.0.0", "--port", "8000", "--debug"]
