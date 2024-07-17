#!/usr/bin/env python3

"""RMQ Producer"""

from Service.Data.caching import Caching
from environment import LoadEnv
from Service.logg import Log
import pika


class RMQProducer:
    def __init__(self):
        self.channel = None
        self.env = LoadEnv()

        self.logging = Log(self.__class__.__name__)
        self.logging.info(f"Instance created")

        self.caching = Caching().get_instance()

    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.env.rmq_user, self.env.rmq_pass)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.env.rmq_host,
                    port=int(self.env.rmq_port),
                    credentials=credentials,
                    virtual_host=self.env.rmq_vhost,
                )
            )
            self.channel = self.connection.channel()
            self.logging.info(f"Connection created.")
            return True
        except Exception as ex:
            self.logging.error(f"Connection error: {ex}")
            self.caching.set("status", "unhealthy: {ex.__cause__}")
            return False

    def produce(self, exchange, routing_key, json_data, correlation_id):
        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json_data,
                properties=pika.BasicProperties(correlation_id=correlation_id),
            )
            self.logging.info(f"Reply sent to: {exchange}")
            return True
        except Exception as ex:
            self.logging.error(f"Error sending reply: {ex}")
            return False
