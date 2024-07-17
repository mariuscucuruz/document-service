from Service.Data.caching import Caching
from environment import LoadEnv
import json
from Service.logg import Log
import pika
import traceback


class RMQConsumer:
    def __init__(self):
        self.channel = None
        self.env = LoadEnv()
        self.logging = Log(self.__class__.__name__)
        self.logging.info("Instance created")
        self.connection = None
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
            self.logging.info("Connection created.")
            return True
        except Exception as ex:
            self.logging.error(f"Connection error: {ex}")
            self.caching.set("status", f"connection: {ex}")
            return False

    def declare_consumer(self, callback):
        try:
            self.channel.basic_consume(
                queue=self.env.rmq_queue,
                on_message_callback=callback,
                auto_ack=True
            )
            self.logging.info("Declared consumer.")
            return True
        except Exception as ex:
            self.logging.error(f"Error declaring consumer: {ex}")
            self.caching.set("status", f"announce: {ex}")
            return False

    def start_consumer(self):
        try:
            self.caching.set("status", "healthy")
            self.logging.info("Started consumer.")
            self.channel.start_consuming()
            return True
        except Exception as ex:
            traceback.print_exc()
            self.logging.error(f"Error whilst consuming: {ex}")
            self.caching.set("status", "unhealthy")
            return False
