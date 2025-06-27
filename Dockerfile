# Official Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL app code to container
COPY . .

# Expose Dash port
EXPOSE 8050

# Run the Dash app
CMD ["python3", "TransientXplorer.py"]

