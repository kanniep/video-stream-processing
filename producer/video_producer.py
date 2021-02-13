import time
import cv2
import sys
from confluent_kafka import SerializingProducer
from video_reader import VideoReader


class VideoProducer:
    def __init__(self, topic='test', client_id='producer1', bootstrap_servers='localhost:9092', video_reader=None):
        self.topic = topic
        self.video_reader = video_reader
        self.kafka_producer = SerializingProducer(
            {'bootstrap.servers': bootstrap_servers,
             'value.serializer': self.video_reader.serialize,
             'queue.buffering.max.messages': 500000})
        self.delivered_records = 0
        self.start_time = 0

    def acked(self, err, msg):
        """Delivery report handler called on
        successful or failed delivery of message
        """
        if err is not None:
            print("Failed to deliver message: {}".format(err))
        else:
            self.delivered_records += 1
        # print(sys.getsizeof(message))

    def produce(self):
        start_time = time.time()
        while (time.time() - start_time < 60 and self.video_reader.online):
            self.kafka_producer.poll(0.0)
            frame = self.video_reader.read()
            if frame is not None:
                self.kafka_producer.produce(
                    topic=self.topic, value=frame, on_delivery=self.acked)
        print("\nFlushing records...")
        self.kafka_producer.flush()
        finished_time = time.time()
        print("MPS: {}".format(self.delivered_records /
                               (finished_time - start_time)))
        self.video_reader.release()
