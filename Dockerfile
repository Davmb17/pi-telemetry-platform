# Using lightweight Python base image
FROM python:3.12-slim

# Setting the working directory inside the container
WORKDIR /app

# Copying python script from local machine to container 
COPY collector.py .

# Running script when the container starts
CMD ["python3", "collector.py"]
