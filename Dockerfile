# Use the official Python image as a base image
FROM paddlepaddle/paddle:2.6.0-gpu-cuda12.0-cudnn8.9-trt8.6

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY . /app/

# Install the required packages
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements_test.txt
# Install torch
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Set environment variables, if necessary
# ENV MY_VARIABLE=value

# Specify the command to run on container start
CMD ["uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
