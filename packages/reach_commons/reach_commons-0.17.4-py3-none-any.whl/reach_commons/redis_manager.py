from functools import cached_property

import redis


class RedisManager:
    """
    # Example of usage
    # redis_manager = RedisManager('your_redis_host', your_redis_port, your_socket_timeout, your_socket_connection_timeout, your_max_retry)
    # redis_manager.add('key', 'value')
    # value = redis_manager.get('key')
    # redis_manager.delete('key')
    """

    def __init__(
        self,
        redis_host,
        redis_port,
        redis_socket_timeout=10,
        redis_socket_connection_timeout=10,
        redis_max_retry=10,
    ):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_socket_timeout = redis_socket_timeout
        self.redis_socket_connection_timeout = redis_socket_connection_timeout
        self.redis_max_retry = redis_max_retry

    @cached_property
    def redis_connection(self):
        connection_pool = redis.ConnectionPool(
            host=self.redis_host,
            port=self.redis_port,
            socket_timeout=self.redis_socket_timeout,
            socket_connect_timeout=self.redis_socket_connection_timeout,
            max_connections=self.redis_max_retry,
        )
        try:
            redis_connection = redis.StrictRedis(connection_pool=connection_pool)
            ok = redis_connection.ping()
            if not ok:
                raise Exception("ERROR: Redis ping failed")
            return redis_connection
        except Exception as ex:
            raise ex

    def add(self, key, value, expire_seconds=None):
        if expire_seconds is not None:
            self.redis_connection.set(key, value, ex=expire_seconds)
        else:
            self.redis_connection.set(key, value)

    def get(self, key):
        return self.redis_connection.get(key)

    def delete(self, key):
        self.redis_connection.delete(key)

    def set(self, name, value, nx=False, ex=None):
        """
        Sets a key-value pair in Redis with optional constraints.

        Parameters:
        - name (str): The key name to set in Redis.
        - value (str): The value to store under the key.
        - nx (bool): If True, sets the key only if it does not already exist (used for locking).
        - ex (int | None): Expiration time in seconds. If provided, the key will automatically expire.

        Returns:
        - bool: True if the key was set successfully, False otherwise (especially when nx=True and key already exists).
        """
        return self.redis_connection.set(name=name, value=value, nx=nx, ex=ex)
