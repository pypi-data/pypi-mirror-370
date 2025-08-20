FROM python:3.12-slim

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY message_sender.py .
COPY config.json .

# Run the application
CMD ["python", "message_sender.py"]