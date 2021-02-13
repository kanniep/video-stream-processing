import asyncio
import grpc

from image_pb2 import ImageInfo, ImageInfoWithMeta
from image_pb2_grpc import DetectorStub


class ProcessingInt:
    def __init__(self, server_url):
        self.server_url = server_url

    def process(self, message):
        pass


class DetectingInt(ProcessingInt):
    def __init__(self, server_url):
        self.server_url = server_url

    def process(self, message: ImageInfo) -> ImageInfoWithMeta:
        with grpc.insecure_channel(self.server_url) as channel:
            return DetectorStub(channel).Detect(message)
