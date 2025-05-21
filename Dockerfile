# Use official Python image as base
FROM python:3.10

# Set working directory inside container
WORKDIR /app

# Copy all files from repo into container
COPY . .

# Give execution permission and run postinstall.sh
RUN chmod +x ./postinstall.sh && ./postinstall.sh

# Command to run your app
CMD ["python", "main.py"]
