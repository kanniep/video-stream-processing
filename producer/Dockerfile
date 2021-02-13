FROM python:3.6

RUN apt update -y && apt install -y \
libsm6 \
libxext6 \
libxrender-dev \
libgl1-mesa-glx

# Install python dependencies
RUN pip install --no-cache-dir opencv-python confluent-kafka gsutil grpcio grpcio-tools

# Create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy contents
COPY . /usr/src/app