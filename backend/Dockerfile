# Use the official Python slim image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file to install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the backend port
EXPOSE 8000

# Run the backend application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
