from environment import LoadEnv
from Service.logg import Log
import redis


class Caching:
    def __init__(self):
        self.env = LoadEnv()
        self.logging = Log(self.__class__.__name__)
        self.logging.info("Redis instance created")

        self.instance = redis.Redis(
            host=self.env.redis_host,
            port=self.env.redis_port
        )

        self.pool = redis.ConnectionPool(
            host=self.env.redis_host,
            port=self.env.redis_port,
            db=0
        )

        self.client = redis.Redis(connection_pool=self.pool)

    def get_instance(self):
        return self.instance

    def get_client(self):
        return self.client
