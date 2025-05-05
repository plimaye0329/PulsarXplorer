# Official Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements (optional at this stage)
COPY requirements.txt requirements.txt

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code (optional if you want live mount instead)
# COPY . .

# Expose Dash port
EXPOSE 8050

# Default command (bash shell)
CMD [ "bash" ]

