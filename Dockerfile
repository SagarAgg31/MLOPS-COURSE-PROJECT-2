ARG COMET_API_KEY
ENV COMET_API_KEY=${COMET_API_KEY}

FROM python:3.8-slim

# Accept API key at build time

# Avoid .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required by TensorFlow
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    libhdf5-dev \
    libprotobuf-dev \
    protobuf-compiler \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Run training (will now have access to COMET_API_KEY)
RUN pip install python-dotenv
RUN python pipeline/training_pipeline.py

# Expose the port
EXPOSE 5000

# Start the app
CMD ["python", "application.py"]
