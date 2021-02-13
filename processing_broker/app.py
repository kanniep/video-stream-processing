import os
from broker import Broker
from processor_int import DetectingInt
import asyncio
import logging
import logging.config
import yaml
import asyncio

import image_pb2
import image_pb2_grpc

with open('common/logger/logging.config.yaml') as file:
    config = yaml.full_load(file)
    logging.config.dictConfig(config)

BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
PRODUCER_TOPIC = os.getenv('KAFKA_PRODUCER_TOPIC')
CONSUMER_TOPIC = os.getenv('KAFKA_CONSUMER_TOPIC')
CLIENT_ID = os.getenv('KAFKA_CLIENT_ID')

PROCESSOR_URL = str(os.getenv('PROCESSOR_URL'))
MAX_ASYNC_CALLS = int(os.getenv('MAX_ASYNC_CALLS'))

if __name__ == '__main__':

    detector = DetectingInt(PROCESSOR_URL)
    broker = Broker(consumer_topic=CONSUMER_TOPIC, producer_topic=PRODUCER_TOPIC,
                    client_id=CLIENT_ID, bootstrap_servers=BOOTSTRAP_SERVERS,
                    consumer_proto_class=image_pb2.ImageInfo, producer_proto_class=image_pb2.ImageInfoWithMeta,
                    processor=detector,
                    max_thread_calls=MAX_ASYNC_CALLS)

    broker.run()
