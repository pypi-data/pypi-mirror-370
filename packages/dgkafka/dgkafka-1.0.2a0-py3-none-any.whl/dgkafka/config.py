from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class SecurityProtocol(str, Enum):
    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"
    SASL_PLAINTEXT = "SASL_PLAINTEXT"
    SASL_SSL = "SASL_SSL"

class KafkaConfig(BaseModel):
    """Base configuration for all Kafka clients"""
    bootstrap_servers: str = Field(..., alias="bootstrap.servers")
    security_protocol: Literal["PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"] = Field(default="SSL",
                                                alias="security.protocol")
    ssl_ca_location: Optional[str] = Field(default=None, alias="ssl.ca.location")
    ssl_certificate_location: Optional[str] = Field(default=None, alias="ssl.certificate.location")
    ssl_key_location: Optional[str] = Field(default=None, alias="ssl.key.location")
    ssl_endpoint_identification_algorithm: Optional[str] = Field(default=None,
                                                                 alias="ssl.endpoint.identification.algorithm")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        protected_namespaces=()
    )

    def get(self) -> Dict[str, Any]:
        """Get config in format suitable for confluent_kafka"""
        return self.model_dump(by_alias=True, exclude_none=True)

    @classmethod
    def set(cls, config_dict: Dict[str, Any]) -> "KafkaConfig":
        """Create config from dictionary"""
        return cls(**config_dict)

class ConsumerConfig(KafkaConfig):
    """Base consumer configuration"""
    group_id: str = Field(..., alias="group.id")
    enable_auto_commit: bool = Field(default=False, alias="enable.auto.commit")
    auto_offset_reset: Literal["earliest", "latest"] = Field(
        default="earliest", alias="auto.offset.reset")
    session_timeout_ms: int = Field(default=10000, alias="session.timeout.ms")
    max_poll_interval_ms: int = Field(default=300000, alias="max.poll.interval.ms")

class ProducerConfig(KafkaConfig):
    """Base producer configuration"""
    acks: Literal["all", "0", "1"] = Field(default="all")
    retries: int = Field(default=0)
    compression_type: str = Field(default="none", alias="compression.type")
    batch_size: int = Field(default=16384, alias="batch.size")
    linger_ms: int = Field(default=0, alias="linger.ms")


class AvroConfigMixin:
    schema_registry_url: str = Field(..., alias="schema.registry.url")
    schema_registry_ssl_ca_location: Optional[str] = Field(
        default=None, alias="schema.registry.ssl.ca.location")
    schema_registry_ssl_certificate_location: Optional[str] = Field(
        default=None, alias="schema.registry.ssl.certificate.location")
    schema_registry_ssl_key_location: Optional[str] = Field(
        default=None, alias="schema.registry.ssl.key.location")


class AvroConsumerConfig(ConsumerConfig, AvroConfigMixin):
    """Avro consumer configuration with Schema Registry support"""

    @classmethod
    def set(cls, config_dict: Dict[str, Any]) -> "AvroConsumerConfig":
        """Create from dictionary with Schema Registry validation"""
        if "schema.registry.url" not in config_dict:
            raise ValueError("schema.registry.url is required for AvroConsumer")
        return cls(**config_dict)

class AvroProducerConfig(ProducerConfig, AvroConfigMixin):
    """Avro producer configuration with Schema Registry support"""

    @classmethod
    def set(cls, config_dict: Dict[str, Any]) -> "AvroProducerConfig":
        """Create from dictionary with Schema Registry validation"""
        if "schema.registry.url" not in config_dict:
            raise ValueError("schema.registry.url is required for AvroProducer")
        return cls(**config_dict)
