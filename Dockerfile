FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY carbon_pulse/ ./carbon_pulse/
COPY dags/ ./dags/
COPY dbt_project.yml profiles.yml ./
COPY models/ ./models/
COPY great_expectations/ ./great_expectations/

# Create data directory
RUN mkdir -p data

# Install dependencies
RUN uv sync --frozen

# Create non-root user
RUN useradd --create-home --shell /bin/bash carbonpulse
RUN chown -R carbonpulse:carbonpulse /app
USER carbonpulse

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uv", "run", "carbon-pulse-api"] 