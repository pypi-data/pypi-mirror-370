# dgkafka

Python package for working with Apache Kafka supporting multiple data formats.

## Installation

```bash
pip install dgkafka
```

For Avro support (requires additional dependencies):

```bash
pip install dgkafka[avro]
```

For Json support (requires additional dependencies):

```bash
pip install dgkafka[json]
```

## Features

- Producers and consumers for different data formats:
  - Raw messages (bytes/strings)
  - JSON
  - Avro (with Schema Registry integration)
- Robust error handling
- Comprehensive operation logging
- Context manager support
- Flexible configuration

## Quick Start

### Basic Producer/Consumer

```python
from dgkafka import KafkaProducer, KafkaConsumer

# Producer
with KafkaProducer(bootstrap_servers='localhost:9092') as producer:
    producer.produce('test_topic', 'Hello, Kafka!')

# Consumer
with KafkaConsumer(bootstrap_servers='localhost:9092', group_id='test_group') as consumer:
    consumer.subscribe(['test_topic'])
    for msg in consumer.consume():
        print(msg.value())
```

### JSON Support

```python
from dgkafka import JsonKafkaProducer, JsonKafkaConsumer

# Producer
with JsonKafkaProducer(bootstrap_servers='localhost:9092') as producer:
    producer.produce('json_topic', {'key': 'value'})

# Consumer
with JsonKafkaConsumer(bootstrap_servers='localhost:9092', group_id='json_group') as consumer:
    consumer.subscribe(['json_topic'])
    for msg in consumer.consume():
        print(msg.value())  # Automatically deserialized JSON
```

### Avro Support

```python
from dgkafka import AvroKafkaProducer, AvroKafkaConsumer

# Producer
value_schema = {
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"}
    ]
}

with AvroKafkaProducer(
    schema_registry_url='http://localhost:8081',
    bootstrap_servers='localhost:9092',
    default_value_schema=value_schema
) as producer:
    producer.produce('avro_topic', {'name': 'Alice', 'age': 30})

# Consumer
with AvroKafkaConsumer(
    schema_registry_url='http://localhost:8081',
    bootstrap_servers='localhost:9092',
    group_id='avro_group'
) as consumer:
    consumer.subscribe(['avro_topic'])
    for msg in consumer.consume():
        print(msg.value())  # Automatically deserialized Avro object
```

## Classes

### Base Classes

- `KafkaProducer` - base message producer
- `KafkaConsumer` - base message consumer

### Specialized Classes

- `JsonKafkaProducer` - JSON message producer (inherits from `KafkaProducer`)
- `JsonKafkaConsumer` - JSON message consumer (inherits from `KafkaConsumer`)
- `AvroKafkaProducer` - Avro message producer (inherits from `KafkaProducer`)
- `AvroKafkaConsumer` - Avro message consumer (inherits from `KafkaConsumer`)

## Configuration

All classes accept standard Kafka configuration parameters:

```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
}
```

Avro classes require additional parameter:
- `schema_registry_url` - Schema Registry URL

## Logging

All classes use `dglog.Logger` for logging. You can provide a custom logger:

```python
from dglog import Logger

logger = Logger()
producer = KafkaProducer(logger_=logger, ...)
```

## Best Practices

1. Always use context managers (`with`) for proper resource cleanup
2. Implement error handling and retry logic for production use
3. Pre-register Avro schemas in Schema Registry
4. Configure appropriate `acks` and `retries` parameters for producers
5. Monitor consumer lag and producer throughput

## Advanced Usage

### Custom Serialization

```python
# Custom Avro serializer
class CustomAvroProducer(AvroKafkaProducer):
    def _serialize_value(self, value):
        # Custom serialization logic
        return super()._serialize_value(value)
```

### Message Headers

```python
# Adding headers to messages
headers = {
    'correlation_id': '12345',
    'message_type': 'user_update'
}

producer.produce(
    topic='events',
    value=message_data,
    headers=headers
)
```

### Error Handling

```python
from confluent_kafka import KafkaException

try:
    with AvroKafkaProducer(...) as producer:
        producer.produce(...)
except KafkaException as e:
    print(f"Kafka error occurred: {e}")
```

## Performance Tips

1. Batch messages when possible (`batch.num.messages` config)
2. Adjust `linger.ms` for better batching
3. Use `compression.type` (lz4, snappy, or gzip)
4. Tune `fetch.max.bytes` and `max.partition.fetch.bytes` for consumers

## License

MIT