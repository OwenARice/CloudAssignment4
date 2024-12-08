# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the inference consumer script to the container
COPY inference_consumer.py /app

# Install required dependencies
RUN pip install --no-cache-dir \
    kafka-python \
    requests \
    numpy \
    Pillow

# Expose port 9092 to connect with Kafka (optional, depending on your needs)
EXPOSE 9092

# Command to run the inference consumer
CMD ["python", "inference_consumer.py"]
