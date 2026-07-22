"""RabbitMQ event publishing for async events."""

import json
import logging
import os
from typing import Optional

import pika

LOG = logging.getLogger(__name__)

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "getting_started.events"


class EventPublisher:
    """Publishes events to RabbitMQ topic exchange."""

    def __init__(self):
        """Initialize the event publisher."""
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def connect(self) -> None:
        """Connect to RabbitMQ and declare exchange."""
        try:
            parameters = pika.URLParameters(RABBITMQ_URL)
            self.connection = pika.BlockingConnection([parameters])
            self.channel = self.connection.channel()

            self.channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="topic",
                durable=True,
            )
            LOG.info("Connected to RabbitMQ at %s", RABBITMQ_URL)
        except Exception as e:
            LOG.warning(
                "Failed to connect to RabbitMQ: %s. Events will not be published.", e
            )
            self.connection = None
            self.channel = None

    def publish(self, routing_key: str, data: dict) -> bool:
        """Publish an event to RabbitMQ.

        Args:
            routing_key: Event routing key (e.g., 'guardrails.scan.completed').
            data: Event data.

        Returns:
            True if published successfully, False if RabbitMQ unavailable.
        """
        if self.channel is None:
            LOG.debug(
                "RabbitMQ not available, skipping event publication: %s", routing_key
            )
            return False

        try:
            self.channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
            )
            LOG.debug("Published event: %s", routing_key)
            return True
        except Exception as e:
            LOG.warning("Failed to publish event %s: %s", routing_key, e)
            return False

    def close(self) -> None:
        """Close the RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            LOG.info("RabbitMQ connection closed")


_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get or create the event publisher singleton."""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
        _publisher.connect()
    return _publisher


def publish_scan_event(
    scan_directory: str,
    total_findings: int,
) -> None:
    """Publish a scan completed event.

    Args:
        scan_directory: Directory that was scanned.
        total_findings: Number of findings.
    """
    publisher = get_event_publisher()
    publisher.publish(
        "guardrails.scan.completed",
        {
            "scan_directory": scan_directory,
            "total_findings": total_findings,
        },
    )


def publish_kv_event(
    event_type: str,
    key: str,
    value: Optional[str] = None,
) -> None:
    """Publish a KV store event.

    Args:
        event_type: 'updated' or 'deleted'.
        key: The key.
        value: The value (for updated events).
    """
    publisher = get_event_publisher()
    routing_key = f"kv.{event_type}"
    data = {"key": key}
    if value is not None:
        data["value"] = value
    publisher.publish(routing_key, data)
