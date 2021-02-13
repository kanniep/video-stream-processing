import os
from video_reader import VideoReader
from video_producer import VideoProducer
import cProfile


CAMERA_ID = os.getenv('CAMERA_ID')
FRAME_WIDTH = int(os.getenv('FRAME_WIDTH'))
FRAME_HEIGHT = int(os.getenv('FRAME_HEIGHT'))
FRAME_RATE = int(os.getenv('FRAME_RATE'))
FRAME_BUFFER_SIZE = int(os.getenv('FRAME_BUFFER_SIZE'))

TOPIC = os.getenv('KAFKA_TOPIC')
BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
CLIENT_ID = os.getenv('KAFKA_CLIENT_ID')

if __name__ == '__main__':

    reader = VideoReader(device_id=CAMERA_ID, frame_size=(
        FRAME_WIDTH, FRAME_HEIGHT), frame_rate=FRAME_RATE, buffer_size=FRAME_BUFFER_SIZE)
    producer = VideoProducer(
        topic=TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS, client_id=CLIENT_ID, video_reader=reader)

    cProfile.run("producer.produce()")
