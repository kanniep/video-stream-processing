import logging
import threading
import time
from collections import deque

from confluent_kafka import DeserializingConsumer, SerializingProducer

import image_pb2
import image_pb2_grpc


class Broker:
    def __init__(self, consumer_topic, producer_topic, client_id, bootstrap_servers,
                 consumer_proto_class, producer_proto_class,
                 processor, max_thread_calls):
        self.consumer_topic = consumer_topic
        self.producer_topic = producer_topic
        self.client_id = client_id
        self.bootstrap_servers = bootstrap_servers
        self.consumer_proto_class = consumer_proto_class
        self.producer_proto_class = producer_proto_class
        self.processor = processor
        self.max_thread_calls = max_thread_calls

        self.kafka_consumer = DeserializingConsumer({'bootstrap.servers': self.bootstrap_servers,
                                                     'group.id': self.client_id,
                                                     'auto.offset.reset': "earliest",
                                                     'value.deserializer': self.derializer})
        self.kafka_consumer.subscribe([self.consumer_topic])

        self.kafka_producer = SerializingProducer({'bootstrap.servers': self.bootstrap_servers,
                                                   'queue.buffering.max.messages': 500000,
                                                   'value.serializer': self.serialize})

        self.thread_queue = deque(maxlen=self.max_thread_calls)
        self.latest_thread_queue_id = 1

    def derializer(self, bytes_message, _):
        message = image_pb2.ImageInfo()
        message.ParseFromString(bytes_message)
        return message

    def serialize(self, message, _):
        return message.SerializeToString()

    def get_thread_id(self):
        result = self.latest_thread_queue_id
        if result == self.max_thread_calls:
            self.latest_thread_queue_id = 1
        else:
            self.latest_thread_queue_id += 1
        return result

    def is_thread_queue_full(self):
        return len(self.thread_queue) == self.max_thread_calls

    def produce_when_ready(self, thread_id, message):
        while self.thread_queue[-1] != thread_id:
            logging.warning("Thread {} got stuck in queue".format(thread_id))
            # time.sleep(0.01)
        self.kafka_producer.poll(0.0)
        self.kafka_producer.produce(
            topic=self.producer_topic, value=message)
        self.thread_queue.pop()

    def call_processor(self, thread_id, value, start_time):
        result = self.processor.process(value)
        self.produce_when_ready(thread_id, result)
        logging.debug("Total time for thead" + str(thread_id) +
                      " is " + str(time.time() - start_time / 1000))

    def run(self):
        while True:
            try:
                if self.is_thread_queue_full():
                    logging.warning(
                        "Thread queue is full, waiting for previous threads to finished")
                    continue

                msg = self.kafka_consumer.poll(1.0)
                if msg is None or msg.value() is None:
                    logging.warning("No messages from kafka")
                    continue

                caller_thread_id = self.get_thread_id()
                caller_thread = threading.Thread(target=self.call_processor, args=(
                    caller_thread_id, msg.value(), msg.timestamp()[1]))
                self.thread_queue.appendleft(caller_thread_id)
                caller_thread.start()

            except KeyboardInterrupt:
                break

        self.kafka_consumer.close()
        self.kafka_producer.flush()
