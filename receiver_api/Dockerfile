FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code
COPY . .

# Expose the port Cloud Run expects
EXPOSE 8080

# Start the app with uvicorn, using port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
