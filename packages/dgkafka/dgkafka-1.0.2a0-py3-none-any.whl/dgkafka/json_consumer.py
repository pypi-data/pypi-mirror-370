from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka.serialization import StringDeserializer
from dglog import Logger
from dgkafka.consumer import KafkaConsumer


class JsonKafkaConsumer(KafkaConsumer):
    def __init__(self, logger_: Logger | None = None, **configs):
        self.consumer: DeserializingConsumer | None = None
        self.schema_registry = {'url': configs.pop('schema.registry.url')}
        self.schema_client = SchemaRegistryClient(self.schema_registry)
        self.deserializer = JSONDeserializer(schema_str=None, schema_registry_client=self.schema_client)

        super(JsonKafkaConsumer, self).__init__(logger_, **configs)

    def init_consumer(self, logger_: Logger | None = None, **configs):
        consumer_conf = {
            **configs,
            'key.deserializer': StringDeserializer('utf_8'),
            'value.deserializer': self.deserializer
        }
        self.logger = logger_ or Logger()
        self.consumer = DeserializingConsumer(consumer_conf)
