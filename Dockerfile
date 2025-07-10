FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Expose port (Railway uses $PORT)
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_ENV=production
ENV PORT=8080

# Start the app
CMD ["python", "lataupe_integrated_app.py"]
