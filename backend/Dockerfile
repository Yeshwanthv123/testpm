# Use an official Python runtime as a parent image
FROM python:3.10-slim
# Set environment variables to prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /backend

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       dos2unix \
       # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# --- START FIX ---
# This ensures the script is copied to /backend/docker-entrypoint.sh
# The '.' copies it to the current WORKDIR (/backend)
COPY docker-entrypoint.sh .

# Fix Windows line endings (CRLF -> LF) using dos2unix
# and make the script executable
RUN dos2unix docker-entrypoint.sh \
    && chmod +x docker-entrypoint.sh
# --- END FIX ---

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/backend/docker-entrypoint.sh"]