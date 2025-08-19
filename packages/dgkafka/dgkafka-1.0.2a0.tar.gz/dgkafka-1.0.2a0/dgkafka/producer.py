import uuid
from typing import Optional, Any

from datetime import datetime, date

from confluent_kafka import Producer, Message
from dgkafka.errors import ProducerNotSetError

import logging
import dglog


class KafkaProducer:
    def __init__(self, logger_: logging.Logger | dglog.Logger | None = None, **configs: Any) -> None:
        """Initialize Kafka producer.

        Args:
            logger_: Optional logger instance
            configs: Kafka producer configuration
        """
        self.producer: Producer | None = None
        self.logger = logger_ if logger_ else dglog.Logger()

        self._delivery_status = {'success': None}

        if isinstance(self.logger, dglog.Logger):
            self.logger.auto_configure()
        self._init_producer(**configs)

    def _init_producer(self, **configs: Any) -> None:
        """Internal method to initialize producer."""
        try:
            self.producer = Producer(configs)
            self.logger.info("[*] Producer initialized successfully")
        except Exception as ex:
            self.logger.error(f"[x] Failed to initialize producer: {ex}")
            raise

    def close(self) -> None:
        """Close the producer connection."""
        if self.producer is not None:
            try:
                self.producer.flush()
                self.logger.info("[*] Producer closed successfully")
            except Exception as ex:
                self.logger.error(f"[x] Error closing producer: {ex}")
                raise
            finally:
                self.producer = None

    def __enter__(self):
        """Context manager entry point."""
        if self.producer is None:
            self._init_producer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()

    def _ensure_producer(self) -> Producer:
        """Ensure producer is initialized."""
        if self.producer is None:
            raise ProducerNotSetError('[!] Producer not initialized!')
        return self.producer

    def delivery_report(self, err: Optional[Any], msg: Message) -> None:
        """Delivery callback for produced messages.

        Args:
            err: Error object if delivery failed
            msg: Delivered message object
        """
        if err is not None:
            self.logger.error(f"[x] Message delivery failed: {err}")
            self.logger.debug(f"[~] Failed message details: {msg}")
            self._delivery_status['success'] = False
        else:
            self.logger.info(
                f"[>] Message delivered to {msg.topic()} [partition {msg.partition()}, offset {msg.offset()}]")
            self._delivery_status['success'] = True

    def produce(
            self,
            topic: str,
            message: str | bytes | dict[str, Any],
            key: str | None = None,
            partition: int | None = None,
            headers: dict[str, bytes] | None = None,
            flush: bool = True,
            flush_timeout: float | None = None
    ) -> bool:
        """Produce a message to Kafka.

        Args:
            topic: Target topic name
            message: Message content (str, bytes or dict)
            key: Message key (optional)
            partition: Specific partition (optional)
            headers: Message headers (optional)
            flush: Immediately flush after producing (default: True)
        """
        producer = self._ensure_producer()
        producer.poll(0)

        self._delivery_status['success'] = None

        # Generate key if not provided
        key = key if key is not None else str(uuid.uuid4())
        key_bytes = key.encode('utf-8')

        # Prepare message value
        if isinstance(message, str):
            value = message.encode('utf-8')
        elif isinstance(message, bytes):
            value = message
        else:  # Assume dict-like object
            try:
                import json
                dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) or isinstance(obj, date) else None
                value = json.dumps(message, ensure_ascii=False, default=dthandler, indent=4).encode('utf-8')
            except Exception as ex:
                self.logger.error(f"[x] Failed to serialize message: {ex}")
                return False

        # Prepare message headers
        headers_list = None
        if headers:
            headers_list = [(k, v if isinstance(v, bytes) else str(v).encode('utf-8'))
                            for k, v in headers.items()]

        # Produce message
        try:
            if not partition:
                producer.produce(
                    topic=topic,
                    value=value,
                    key=key_bytes,
                    on_delivery=self.delivery_report,
                    headers=headers_list
                )
            else:
                producer.produce(
                    topic=topic,
                    value=value,
                    key=key_bytes,
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
        except Exception as ex:
            self.logger.error(f"[x] Failed to produce message: {ex}")
            return False

    def flush(self, timeout: float | None = None) -> int | None:
        """Wait for all messages to be delivered.

        Args:
            timeout: Maximum time to wait (seconds)
        """
        producer = self._ensure_producer()
        try:
            remaining = producer.flush(timeout)
            if remaining > 0:
                self.logger.warning(f"[!] {remaining} messages remain undelivered")
            return remaining
        except Exception as ex:
            self.logger.error(f"[x] Flush failed: {ex}")
            raise