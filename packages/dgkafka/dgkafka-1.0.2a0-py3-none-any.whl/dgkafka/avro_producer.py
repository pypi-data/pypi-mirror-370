from typing import Optional, Union, Dict, Any
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient

import dglog
import logging

from dgkafka.producer import KafkaProducer


class AvroKafkaProducer(KafkaProducer):
    """Kafka producer with Avro schema support using Schema Registry."""

    def __init__(
            self,
            default_key_schema: str | None = None,
            default_value_schema: str | None = None,
            logger_: logging.Logger | dglog.Logger | None = None,
            **configs: Any
    ) -> None:
        """
        Initialize Avro producer.

        Args:
            schema_registry_url: URL of Schema Registry
            default_key_schema: Default Avro schema for message keys
            default_value_schema: Default Avro schema for message values
            logger_: Optional logger instance
            configs: Kafka producer configuration
        """
        self.schema_registry_url = configs.get('schema.registry.url')
        assert self.schema_registry_url is not None, "schema.registry.url is required"

        self.default_key_schema = default_key_schema
        self.default_value_schema = default_value_schema
        self.schema_registry_client = CachedSchemaRegistryClient(url=self.schema_registry_url)
        super().__init__(logger_=logger_, **configs)

    def _init_producer(self, **configs: Any) -> None:
        """Initialize AvroProducer instance."""
        try:
            self.producer = AvroProducer(
                config=configs,
                default_key_schema=self.default_key_schema,
                default_value_schema=self.default_value_schema
            )
            self.logger.info("[*] Avro producer initialized successfully")
        except Exception as ex:
            self.logger.error(f"[x] Failed to initialize avro producer: {ex}")
            raise

    def produce(
            self,
            topic: str,
            value: dict[str, Any] | Any,
            key: dict[str, Any] | str | None  = None,
            value_schema: dict[str, Any] | None = None,
            key_schema: dict[str, Any] | None = None,
            partition: int | None = None,
            headers: dict[str, bytes] | None = None,
            flush: bool = True,
            flush_timeout: float | None = None
    ) -> None:
        """
        Produce Avro-encoded message to Kafka.

        Args:
            topic: Target topic name
            value: Message value (must match Avro schema)
            key: Message key (optional)
            value_schema: Avro schema for message value (optional)
            key_schema: Avro schema for message key (optional)
            partition: Specific partition (optional)
            headers: Message headers (optional)
            flush: Immediately flush after producing (default: True)
        """
        producer = self._ensure_producer()
        producer.poll(0)

        self._delivery_status['success'] = None

        # Prepare headers
        headers_list = None
        if headers:
            headers_list = [(k, v if isinstance(v, bytes) else str(v).encode('utf-8'))
                            for k, v in headers.items()]

        try:
            if not partition:
                producer.produce(
                    topic=topic,
                    value=value,
                    value_schema=value_schema,
                    key=key,
                    key_schema=key_schema,
                    on_delivery=self.delivery_report,
                    headers=headers_list
                )
            else:
                producer.produce(
                    topic=topic,
                    value=value,
                    value_schema=value_schema,
                    key=key,
                    key_schema=key_schema,
                    partition=partition,
                    on_delivery=self.delivery_report,
                    headers=headers_list
                )

            if flush:
                remaining = self.flush(flush_timeout)  # timeout 1 second
                if remaining > 0:
                    return False

            # Если flush=True, статус должен быть установлен к этому моменту
            if flush and self._delivery_status['success'] is not None:
                return self._delivery_status['success']

            # Если flush=False, мы не можем гарантировать доставку, возвращаем True
            # (так как технически ошибки пока нет)
            return True

        except SerializerError as ex:
            self.logger.error(f"[x] Avro serialization failed: {ex}")
            return False
        except Exception as ex:
            self.logger.error(f"[x] Failed to produce Avro message: {ex}")
            return False

    def get_schema(self, subject: str, version: int = 1) -> Dict[str, Any]:
        """Get Avro schema from Schema Registry."""
        return self.schema_registry_client.get_schema(subject, version)

    def get_latest_schema(self, subject: str) -> Dict[str, Any]:
        """Get latest version of schema for given subject."""
        return self.schema_registry_client.get_latest_schema(subject)[1]