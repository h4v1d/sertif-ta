# Base image dengan Python 3.11 (Multi-arch compatible)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for WeasyPrint
# libcairo2, libpango-1.0-0, libpangocairo-1.0-0, libgdk-pixbuf2.0-0, libffi-dev, shared-mime-info
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
# Install pip dependencies (assuming no poetry/lock file, using direct pip install from pyproject or requirements)
# Since the user mentioned pyproject.toml, we'll try to install from it.
# If standard pip install . works for pyproject.toml dependencies:
RUN pip install --no-cache-dir .

# Copy project files
COPY . .

# Create output directory for PDFs
RUN mkdir -p output

# Expose port 8002
EXPOSE 8002

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
