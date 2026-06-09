from .connection_options import connection_options
import redis

class RedisConnection:

    def __init__(self):
        self.host = connection_options['HOST']
        self.port = connection_options['PORT']
        self.db = connection_options['DB']

    def connect(self):
        redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db
        )

        return redis_client