# Multi-stage Docker build for MAOS
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r maos && useradd -r -g maos maos

# Development stage
FROM base as development

# Install development dependencies
RUN pip install poetry

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --with dev,deployment

# Copy source code
COPY . .

# Change ownership to app user
RUN chown -R maos:maos /app
USER maos

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "maos.server"]

# Production stage
FROM base as production

# Install production dependencies
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY setup.py ./
COPY README.md ./

# Install MAOS package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/logs /app/checkpoints /app/data

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Change ownership to app user
RUN chown -R maos:maos /app
USER maos

# Health check - disabled for now since there's no server
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command - just keep container running
CMD ["python", "-c", "import time; print('MAOS Container Running - Use docker exec to run commands'); time.sleep(86400)"]

# Worker stage
FROM production as worker

# Override default command for worker - just keep running
CMD ["python", "-c", "import time; print('MAOS Worker Running'); time.sleep(86400)"]

# CLI stage  
FROM production as cli

# Override default command for CLI
ENTRYPOINT ["bash"]