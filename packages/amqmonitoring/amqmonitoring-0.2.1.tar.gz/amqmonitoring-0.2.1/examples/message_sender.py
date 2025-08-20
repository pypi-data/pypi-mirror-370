import pika
import json
import time
import os
import logging

from random import randint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MessageSender:
    def __init__(
            self,
            host: str | None = None,
            port: int | None = None,
            username: str | None = None,
            password: str | None = None,
            message_interval: str | None = None
    ):
        self.host = host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = port or int(os.getenv('RABBITMQ_PORT', '5672'))
        self.username = username or os.getenv('RABBITMQ_USER', 'guest')
        self.password = password or os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.message_interval = message_interval or int(
            os.getenv('MESSAGE_INTERVAL', '1'))

        self.connection = None
        self.channel = None
        # Keep track of declared exchanges and queues to avoid redeclaring
        self.declared_exchanges = set()
        self.declared_queues = set()

    @staticmethod
    def generate_message():
        return {f'key{randint(0,3)}': f'value{randint(0,5)}'}

    def connect(self) -> bool:
        """Establish connection to RabbitMQ"""
        max_retries = 10
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(self.username,
                                                    self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )

                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
                return True

            except Exception as e:
                logger.error(
                    f"Connection attempt {attempt + 1}/{max_retries}"
                    f" failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        "Max retries reached. Could not connect to RabbitMQ")
        return False

    def ensure_exchange_and_queue(self, exchange_name, queue_name, routing_key):
        """Ensure exchange and queue exist and are bound"""
        try:
            # Declare exchange if not already declared
            if exchange_name not in self.declared_exchanges:
                self.channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type='direct',
                    durable=True
                )
                self.declared_exchanges.add(exchange_name)
                logger.info(f"Exchange '{exchange_name}' declared")

            # Declare queue if not already declared
            if queue_name not in self.declared_queues:
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.declared_queues.add(queue_name)
                logger.info(f"Queue '{queue_name}' declared")

            # Bind queue to exchange with routing key
            self.channel.queue_bind(
                exchange=exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )
            logger.info(f"Queue '{queue_name}' bound to exchange '{exchange_name}' with routing key '{routing_key}'")

        except Exception as e:
            logger.error(f"Failed to ensure exchange and queue: {e}")
            raise

    def send_message(self, message_data):
        """Send message using key as exchange and value as routing key/queue name"""
        try:
            # Extract key and value from the message
            key = list(message_data.keys())[0]  # First key becomes exchange name
            value = message_data[key]  # Value becomes routing key and queue name

            exchange_name = key
            routing_key = value
            queue_name = value  # Queue name same as routing key/value

            # Ensure exchange and queue exist
            self.ensure_exchange_and_queue(exchange_name, queue_name, routing_key)

            # Convert message to JSON for sending
            message_json = json.dumps(message_data)

            # Publish message
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

            logger.info(f"Message sent to exchange '{exchange_name}' -> queue '{queue_name}' with routing key '{routing_key}'")
            logger.info(f"Message content: {message_json}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def run(self):
        """Main loop to send periodic messages"""
        logger.info(f"Starting dynamic message sender...")
        logger.info(f"Interval: {self.message_interval} seconds")
        logger.info("Each message will create/use exchange=key, routing_key=value, queue=value")

        if not self.connect():
            return

        try:
            while True:
                message = self.generate_message()

                if self.send_message(message):
                    logger.info(
                        f"Next message in {self.message_interval} seconds...")
                else:
                    logger.error(
                        "Failed to send message, attempting to reconnect...")
                    if not self.connect():
                        break

                time.sleep(self.message_interval)

        except KeyboardInterrupt:
            logger.info("Stopping message sender...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Close connections"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Connection closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    sender = MessageSender()
    sender.run()