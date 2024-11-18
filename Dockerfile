FROM python:3

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file to the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port your application runs on
EXPOSE 3001

# Command to run the main Python file
CMD ["python", "./main.py"]
