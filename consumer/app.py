import os
from video_presenter import VideoPresenter
from video_comsumer import VideoConsumer
import logging
import logging.config
import yaml

TOPIC = os.getenv('KAFKA_TOPIC')
BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
CLIENT_ID = os.getenv('KAFKA_CLIENT_ID')

with open('common/logger/logging.config.yaml') as file:
    config = yaml.full_load(file)
    logging.config.dictConfig(config)

if __name__ == '__main__':

    presenter = VideoPresenter()
    producer = VideoConsumer(
        topic=TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS, client_id=CLIENT_ID, video_presenter=presenter)

    producer.consume()
