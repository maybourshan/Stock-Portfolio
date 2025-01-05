# Use Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 5003
EXPOSE 5003

# Run the application
CMD ["python", "capital_gains.py"]
