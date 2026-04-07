# Multi-stage build for AI Operations Assistant Environment

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "AI Operations Assistant Environment - OpenEnv Implementation"\n\
echo "==============================================================="\n\
echo ""\n\
python validate_openenv.py\n\
echo ""\n\
echo "Validation complete"\n\
echo ""\n\
python -c "from env.environment import AIOperationsEnvironment; print(\"✓ Environment imported successfully\")"\n\
python -c "from tasks.easy import EasyEmailClassificationTask; print(\"✓ Easy task imported successfully\")"\n\
python -c "from tasks.medium import MediumSupportHandlingTask; print(\"✓ Medium task imported successfully\")"\n\
python -c "from tasks.hard import HardFullOperationsTask; print(\"✓ Hard task imported successfully\")"\n\
python -c "from baseline.agent import BaselineAgent; print(\"✓ Baseline agent imported successfully\")"\n\
echo ""\n\
echo "Running baseline evaluation..."\n\
echo ""\n\
python baseline/run.py\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Labels for metadata
LABEL maintainer="AI Research Team"
LABEL description="AI Operations Assistant Environment - OpenEnv Implementation"
LABEL version="1.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from env.environment import AIOperationsEnvironment; print('OK')" || exit 1

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Expose port for potential future use (Hugging Face Space)
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
