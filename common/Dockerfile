FROM python

RUN apt update && apt install -y protobuf-compiler
RUN python -m pip install grpcio grpcio-tools
COPY protos /protos
WORKDIR /protos