# Step 1: Use the official Python image from Docker Hub as the base image
FROM python:3.13-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file to the container
COPY chat_server/requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application files into the container
COPY . /app

# Step 6: Expose the port that the Flask app will run on
EXPOSE 5000

# Step 7: Run app.py when the container launches
CMD ["python", "chat_server/server.py"]
