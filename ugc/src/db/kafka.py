from core.config import settings
from kafka import KafkaProducer

kafka_producer = KafkaProducer(bootstrap_servers=settings.kafka.bootstrap_servers)
