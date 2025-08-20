#!/usr/bin/env python3
"""
AMQP Queue Listener using Pika.
"""
import os
import pika
import sys
import logging

from typing import Callable
from pika.exceptions import AMQPConnectionError

# Get logger.
logger = logging.getLogger(__name__)


class AMQPListener:
    def __init__(self, host: str | None = None,
                 port: str | None = None, queue_name: str | None = None):
        """
        Initialize the AMQP listener for AMQP traces_on queues.
        """
        self.host = host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = port or int(os.getenv('RABBITMQ_PORT', '5672'))
        self.queue_name = queue_name or os.getenv('RABBITMQ_QUEUE', 'trace')
        self.connection = None
        self.channel = None

    def connect(self, user: str | None = None,
                password: str | None = None):
        """Establish connection to RabbitMQ server."""

        user = user or os.getenv('RABBITMQ_USER', 'guest')
        password = password or os.getenv('RABBITMQ_PASSWORD', 'guest')

        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host, port=self.port,
                    credentials=pika.PlainCredentials(
                        username=user,
                        password=password
                    ),
                )
            )
            self.channel = self.connection.channel()

            # Declare the queue (create if it doesn't exist).
            self.channel.queue_declare(queue=self.queue_name, durable=True)

            logger.info(f"Connected to RabbitMQ server at {self.host}.")
            logger.info(f"Queue '{self.queue_name}' declared.")

        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            sys.exit(1)

    @staticmethod
    def process_message(ch, method, properties, body):
        """
        Process received message, this function just prints the message.
        """
        message = body.decode('utf-8')
        print(f"Received message: {message}")

        # Acknowledge the message (remove from queue).
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Message processed and acknowledged.")

    def start_listening(self, callback: Callable):
        """Start listening to the queue."""
        if not self.connection or not self.channel:
            logger.error("Not connected to RabbitMQ. Call connect() first.")
            return

        # Set up consumer.
        self.channel.basic_qos(
            prefetch_count=1)  # Process one message at a time.
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback or self.process_message
        )

        logger.info(
            f"Waiting for messages from queue"
            f" '{self.queue_name}'. To exit press CTRL+C")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
            self.connection.close()
            logger.info("Connection closed")
