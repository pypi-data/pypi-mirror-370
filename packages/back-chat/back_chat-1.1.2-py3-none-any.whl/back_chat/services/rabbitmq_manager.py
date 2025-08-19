import asyncio
from typing import Optional

from aio_pika import connect, Message, Channel, Queue
from aio_pika.exceptions import AMQPConnectionError


class RabbitMQManager:
    """
    Asynchronous manager for interacting with RabbitMQ using `aio-pika`.

    This class provides functionality to connect, publish, and consume
    messages from RabbitMQ queues or exchanges. It includes built-in
    retry logic and optional WebSocket broadcasting support for
    real-time notifications.

    :param rabbitmq_url: Connection URL for RabbitMQ.
    :param manager: WebSocket manager instance used for broadcasting messages
    to clients.
    :param max_retries: Maximum number of retry attempts for connecting to
    RabbitMQ.
    :param logger: Optional logger for debug and error logging.
    """

    def __init__(self, rabbitmq_url: str, manager, max_retries: int = 3,
                 logger=None):
        self.rabbitmq_url = rabbitmq_url
        self.manager = manager
        self.max_retries = max_retries
        self.connection = None
        self.channel: Optional[Channel] = None
        self.queue: Optional[Queue] = None
        self.logger = logger

    async def connect(self) -> bool:
        """
        Attempt to establish a connection with RabbitMQ, retrying on failure.

        :return: True if the connection is successful, False otherwise.
        """
        for attempt in range(self.max_retries):
            try:
                self.connection = await connect(self.rabbitmq_url)
                self.channel = await self.connection.channel()
                return True
            except AMQPConnectionError as e:
                if self.logger:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2)
        await self.manager.broadcast("Redundancy service is not available.")
        return False

    async def publish_message(self, queue_name: str, message: str):
        """
        Publish a message to a RabbitMQ queue.

        :param queue_name: Name of the target queue.
        :param message: The message string to publish.
        """
        if not self.channel:
            if self.logger:
                self.logger.warning(
                    "No RabbitMQ channel available. Attempting to reconnect..."
                )
            if not await self.connect():
                return

        try:
            await self.channel.default_exchange.publish(
                Message(body=message.encode()),
                routing_key=queue_name,
            )
            if self.logger:
                self.logger.debug(
                    f"Message published to {queue_name}: {message}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to publish message: {e}")

    async def publish_message_to_exchange(
            self, exchange_name: str, message: str, routing_key: str = ''):
        """
        Publish a message to a RabbitMQ exchange.

        :param exchange_name: Name of the exchange.
        :param message: The message string to publish.
        :param routing_key: Optional routing key.
        """
        if not self.channel:
            if self.logger:
                self.logger.warning(
                    "No RabbitMQ channel available. Attempting to reconnect..."
                )
            if not await self.connect():
                return

        try:
            exchange = await self.channel.declare_exchange(
                exchange_name, type='fanout')
            await exchange.publish(
                Message(body=message.encode()),
                routing_key=routing_key
            )
            if self.logger:
                self.logger.debug(
                    f"Message published to exchange "
                    f"{exchange_name}: {message}")
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to publish message to exchange: {e}")

    async def consume_messages(self, queue_name: str):
        """
        Consume messages from a RabbitMQ queue and broadcast them via
        WebSockets.

        :param queue_name: Name of the queue to consume from.
        """
        if not self.channel:
            if self.logger:
                self.logger.warning(
                    "No RabbitMQ channel available. Attempting to reconnect..."
                )
            if not await self.connect():
                return

        try:
            self.queue = await self.channel.declare_queue(
                queue_name, durable=True)
            async for message in self.queue:
                async with message.process():
                    if self.logger:
                        self.logger.debug(
                            f"Received message: {message.body.decode()}")
                    await self.manager.broadcast(message.body.decode())
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to consume messages: {e}")
            await self.manager.broadcast(
                "Redundancy service is not available.")

    async def consume_messages_from_exchange(self, exchange_name: str):
        """
        Consume messages from a RabbitMQ exchange and broadcast them via
        WebSockets.

        :param exchange_name: Name of the exchange to consume from.
        """
        if not self.channel:
            if self.logger:
                self.logger.warning(
                    "No RabbitMQ channel available. Attempting to reconnect..."
                )
            if not await self.connect():
                return

        try:
            exchange = await self.channel.declare_exchange(
                exchange_name, type='fanout')
            queue = await self.channel.declare_queue('', exclusive=True)
            await queue.bind(exchange)
            async for message in queue:
                async with message.process():
                    await self.manager.broadcast(message.body.decode())
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to consume messages from exchange: {e}")
            await self.manager.broadcast(
                "Redundancy service is not available.")
