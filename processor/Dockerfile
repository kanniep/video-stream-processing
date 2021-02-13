# Start FROM Nvidia PyTorch image https://ngc.nvidia.com/catalog/containers/nvidia:pytorch
FROM nvcr.io/nvidia/pytorch:20.12-py3

# Install linux packages
RUN apt update && apt install -y screen libgl1-mesa-glx

# Install python dependencies
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gsutil grpcio grpcio-tools

# Create working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy contents
COPY . /usr/src/app

# Copy weights
RUN python3 -c "from models import *; \
    from utils.google_utils import attempt_download; \
    attempt_download('weights/yolov5s.pt')"
# attempt_download('weights/yolov5m.pt'); \
# attempt_download('weights/yolov5l.pt')"

CMD ["python", "server.py"]