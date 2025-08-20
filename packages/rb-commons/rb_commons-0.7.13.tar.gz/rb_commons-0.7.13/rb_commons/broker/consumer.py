from aio_pika import ExchangeType, IncomingMessage
from rb_commons.configs.rabbitmq import RabbitMQConnection


class BaseRabbitMQConsumer:
    def __init__(self, exchange_name: str, queue_name: str, routing_key: str):
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key

    async def setup(self, channel):
        exchange = await channel.declare_exchange(self.exchange_name, ExchangeType.DIRECT, durable=True)
        queue = await channel.declare_queue(self.queue_name, durable=True)
        await queue.bind(exchange, routing_key=self.routing_key)
        return queue

    async def consume(self):
        async with RabbitMQConnection.get_channel() as channel:
            queue = await self.setup(channel)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self.process_message(message)

    async def process_message(self, message: IncomingMessage):
        async with message.process():
            await self.handle_message(message.body.decode())

    async def handle_message(self, body: str):
        raise NotImplementedError("This method should be overridden by subclasses.")