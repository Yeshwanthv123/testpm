FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /backend

# Combine RUN commands and clean up in the same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY app/ ./app/
COPY PM_Questions_8000_expanded_clean_final5.csv .
COPY docker-entrypoint.sh .

RUN dos2unix docker-entrypoint.sh && \
    chmod +x docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/backend/docker-entrypoint.sh"]