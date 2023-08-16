FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application to the container
COPY . /app/

# Set Streamlit's settings
ENV STREAMLIT_SERVER_PORT 80

# Command to run the app
CMD ["streamlit", "run", "youtube2.py"]
