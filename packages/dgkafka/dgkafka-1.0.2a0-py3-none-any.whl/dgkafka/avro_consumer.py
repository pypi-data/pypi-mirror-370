from typing import Any, Iterator

from dgkafka.consumer import KafkaConsumer

from confluent_kafka import Message
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient

import logging
import dglog


class AvroKafkaConsumer(KafkaConsumer):
    """Kafka consumer with Avro schema support using Schema Registry."""

    def __init__(self, logger_: logging.Logger | dglog.Logger | None = None, **configs: Any) -> None:
        """
        Initialize Avro consumer.

        Args:
            schema_registry_url: URL of Schema Registry
            logger_: Optional logger instance
            configs: Kafka consumer configuration
        """
        self.schema_registry_url = configs.get('schema.registry.url')
        assert self.schema_registry_url is not None, "schema.registry.url is required"

        self.schema_registry_client = CachedSchemaRegistryClient(url=self.schema_registry_url)
        super().__init__(logger_=logger_, **configs)

    def _init_consumer(self, **configs: Any) -> None:
        """Initialize AvroConsumer instance."""
        try:
            self.consumer = AvroConsumer(configs)
            self.logger.info("[*] Avro consumer initialized successfully")
        except Exception as ex:
            self.logger.error(f"[x] Failed to initialize avro consumer: {ex}")
            raise

    def consume(self, num_messages: int = 1, timeout: float = 1.0, decode_: bool = False, **kwargs: Any) -> Iterator[str | bytes | Message | None]:
        """
        Consume Avro-encoded messages.

        Args:
            num_messages: Maximum number of messages to consume
            timeout: Poll timeout in seconds
            kwargs: Additional arguments

        Yields:
            Deserialized Avro messages as dictionaries or Message objects on error
        """
        consumer = self._ensure_consumer()

        for _ in range(num_messages):
            msg = self._consume(consumer, timeout)
            try:
                if msg is None:
                    continue
                yield msg.value() if decode_ else msg
            except SerializerError as e:
                self.logger.error(f"[x] Avro deserialization failed: {e}")
                yield msg  # Return raw message on deserialization error
            except Exception as ex:
                self.logger.error(f"[!] Unexpected error: {ex}")
                continue

    def get_schema(self, subject: str, version: int = 1) -> dict[str, Any]:
        """Get Avro schema from Schema Registry."""
        return self.schema_registry_client.get_schema(subject, version)

    def get_latest_schema(self, subject: str) -> dict[str, Any]:
        """Get latest version of schema for given subject."""
        return self.schema_registry_client.get_latest_schema(subject)[1]
