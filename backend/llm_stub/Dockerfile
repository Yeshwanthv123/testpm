# Use official Python image (lightweight)
FROM python:3.10-slim

WORKDIR /app

# Copy Python requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy wrapper
COPY ollama_wrapper.py .

# Expose Flask wrapper port only (Ollama is on host)
EXPOSE 5000

# Run the Flask app
CMD ["python", "ollama_wrapper.py"]
