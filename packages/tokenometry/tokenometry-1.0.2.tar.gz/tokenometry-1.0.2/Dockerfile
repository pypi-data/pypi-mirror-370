# Use an official lightweight Python image as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt.

# Install any needed packages specified in requirements.txt
# --no-cache-dir ensures we don't store the pip cache, keeping the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application script into the container at /app
COPY milestone_1.py.

# Define the command to run your application
CMD ["python", "milestone_1.py"]
