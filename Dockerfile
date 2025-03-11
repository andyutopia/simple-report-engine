# Use official Python slim base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt update && apt install -y \
    libpango1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY report_logger.py .
COPY utils.py .
COPY constants.py .

# Create directories for logs, templates, and trays
RUN mkdir -p logs
RUN mkdir -p templates
RUN mkdir -p trays

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]