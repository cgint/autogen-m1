# Use an official Python runtime as a parent image
FROM python:3.11-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /usr/src/app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Run the script when the container launches
CMD ["python", "./main.py"]
