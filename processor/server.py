import logging
import asyncio
import grpc
import torch
import cv2
import numpy as np
from timer import Timer

import image_pb2
import image_pb2_grpc

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = torch.hub.load('ultralytics/yolov5', 'yolov5s',
                       pretrained=True).to(device)
names = model.module.names if hasattr(model, 'module') else model.names


class Detector(image_pb2_grpc.DetectorServicer):

    async def Detect(self, request: image_pb2.ImageInfo,
                     context: grpc.aio.ServicerContext
                     ) -> image_pb2.ImageInfoWithMeta:
        with Timer() as timer:
            images = [cv2.imdecode(np.frombuffer(
                request.image, dtype=np.uint8), cv2.IMREAD_UNCHANGED)]
            results = model(images).xyxy[0]
            detections = [image_pb2.Detection(category=names[int(detection[5].item())], confidence=detection[4].item(), x1=detection[0].item(),
                                              y1=detection[1].item(), x2=detection[2].item(), y2=detection[3].item()) for i, detection in enumerate(results)]
        return image_pb2.ImageInfoWithMeta(detections=detections, image_info=request)


async def serve() -> None:
    server = grpc.aio.server()
    image_pb2_grpc.add_DetectorServicer_to_server(Detector(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
