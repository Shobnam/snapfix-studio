# Use official Python image as base
FROM python:3.10

# Set working directory inside container
WORKDIR /app

# Copy all files from repo into container
COPY . .

# Install Node.js and npm (Debian-based)
RUN apt-get update && apt-get install -y nodejs npm

# Give execution permission and run postinstall.sh (which runs npm commands)
RUN chmod +x ./postinstall.sh && ./postinstall.sh

# Install Python dependencies (if you have requirements.txt)
RUN pip install -r requirements.txt

# Command to run your app
CMD ["python", "main.py"]

