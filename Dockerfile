# Use the official Python image as a base
FROM python:3.12-slim

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y firefox-esr && \
    apt-get install -y wget && \
    apt-get install -y libgtk-3-0 libdbus-glib-1-2 && \
    apt-get install -y xvfb && \
    apt-get clean

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the script into the container
COPY *.py /app/

# Set the working directory
WORKDIR /app

# Run the script
CMD ["python", "main.py"]
