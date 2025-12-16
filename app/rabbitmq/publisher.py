import json
import pika
from typing import Dict, Any
from app.core.config import settings


class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    def _connect(self):
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
            raise

    def publish_task(self, task_data: Dict[str, Any]) -> bool:
        try:
            if not self.connection or self.connection.is_closed:
                self._connect()

            message = json.dumps(task_data)
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.RABBITMQ_QUEUE,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            return True
        except Exception as e:
            print(f"Error publishing task: {e}")
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            return False

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()


publisher = RabbitMQPublisher()

