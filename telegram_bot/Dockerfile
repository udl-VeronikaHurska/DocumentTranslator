# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory
WORKDIR /telegram_bot

# Copy the current directory contents into the container
COPY . /telegram_bot

# Install any needed packages specified in requirements.txt
RUN pip install  -r requirements.txt

# Run bot.py when the container launches
CMD ["python", "main.py"]
