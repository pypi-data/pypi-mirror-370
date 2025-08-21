from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: v.encode('utf-8')
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_message(self, topic: str, message: str):
        try:
            await self.producer.send(topic, message)
            print(f"Sent to {topic}: {message}")
        except Exception as e:
            print(f"Kafka send error: {e}")

