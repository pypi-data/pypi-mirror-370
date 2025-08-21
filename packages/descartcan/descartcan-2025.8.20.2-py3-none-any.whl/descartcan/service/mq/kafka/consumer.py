import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from typing import Dict, Any, Callable, Optional, List, Union
from descartcan.utils.log import logger


class KafkaEventRouter:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.routes = {}
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumers = []
        self.running = False

    def on(self, topic: str, group_id: str = None):
        def decorator(func):
            if topic not in self.routes:
                self.routes[topic] = []

            self.routes[topic].append({
                "handler": func,
                "group_id": group_id or f"group-{func.__name__}"
            })
            return func

        return decorator

    async def publish(self, topic: str, message: Union[str, bytes, dict], key: bytes = None):
        if not self.producer:
            raise RuntimeError("Kafka producer not started. Call 'start()' first.")

        if isinstance(message, dict):
            import json
            message = json.dumps(message).encode('utf-8')
        elif isinstance(message, str):
            message = message.encode('utf-8')

        await self.producer.send_and_wait(topic, message, key=key)
        logger.info(f"[KafkaRouter] Published message to '{topic}'")

    async def _consume_messages(self, topic: str, handlers: List[Dict[str, Any]]):
        for handler_config in handlers:
            handler = handler_config["handler"]
            group_id = handler_config["group_id"]

            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset="earliest"
            )

            self.consumers.append(consumer)
            await consumer.start()

            logger.info(f"[KafkaRouter] Bound {handler.__name__} to topic '{topic}' with group '{group_id}'")
            asyncio.create_task(self._process_messages(consumer, topic, handler))

    async def _process_messages(self, consumer, topic: str, handler: Callable):
        try:
            async for msg in consumer:
                try:
                    await handler(
                        msg,
                        topic=topic,
                        kafka_router=self
                    )
                except Exception as e:
                    logger.info(f"[KafkaRouter] Error processing message: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.info(f"[KafkaRouter] Consumer error: {e}")

    async def start(self):
        if self.running:
            return

        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()

        for topic, handlers in self.routes.items():
            await self._consume_messages(topic, handlers)

        self.running = True
        logger.info("[KafkaRouter] Started")

    async def stop(self):
        if not self.running:
            return

        for consumer in self.consumers:
            await consumer.stop()
        self.consumers = []

        if self.producer:
            await self.producer.stop()
            self.producer = None

        self.running = False
        logger.info("[KafkaRouter] Stopped")


kafka_event_router = KafkaEventRouter()
