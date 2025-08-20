from contextlib import asynccontextmanager
from aio_pika import connect_robust, Message, ExchangeType
from rb_commons.configs.config import configs

class RabbitMQConnection:
    _connection = None
    _channel = None

    @classmethod
    @asynccontextmanager
    async def get_channel(cls):
        if not cls._connection:
            cls._connection = await connect_robust(configs.RABBITMQ_URL)
            cls._channel = await cls._connection.channel()

        try:
            yield cls._channel
        finally:
            pass

    @classmethod
    async def close(cls):
        if cls._connection:
            await cls._connection.close()
            cls._connection = None
            cls._channel = None