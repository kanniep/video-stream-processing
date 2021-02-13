import logging

from confluent_kafka import DeserializingConsumer

import image_pb2
from video_presenter import VideoPresenter


class VideoConsumer:
    """
    high level support for doing this and that.
    """

    def __init__(self, topic='test', client_id='consumer1', bootstrap_servers='localhost:9092', video_presenter=VideoPresenter()):
        self.topic = topic
        self.video_presenter = video_presenter
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id

        self.kafka_consumer = DeserializingConsumer({'bootstrap.servers': self.bootstrap_servers,
                                                     'group.id': self.client_id,
                                                     'auto.offset.reset': "earliest",
                                                     'value.deserializer': self.derializer})
        self.kafka_consumer.subscribe([self.topic])

    def derializer(self, bytes_message, _):
        message = image_pb2.ImageInfoWithMeta()
        message.ParseFromString(bytes_message)
        return message

    def consume(self):
        while True:
            try:
                message = self.kafka_consumer.poll(1.0)
                if message is None or message.value() is None:
                    logging.warning("No messages from kafka")
                    continue

                self.video_presenter.show(message.value())

            except KeyboardInterrupt:
                break
