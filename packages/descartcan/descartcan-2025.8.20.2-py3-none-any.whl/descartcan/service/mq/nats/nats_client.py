
import asyncio
import json
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from descartcan.utils.log import logger


class NATSClient:

    def __init__(self, servers=None, name="nats-client"):
        if servers is None:
            servers = ["nats://127.0.0.1:4222"]
        self.nc = NATS()
        self.servers = servers
        self.name = name
        self.connected = False

    async def connect(self):
        if not self.connected:
            await self.nc.connect(servers=self.servers, name=self.name)
            self.connected = True
            logger.info(f"[NATS] Connected to {self.servers}")

    async def publish(self, subject: str, message: dict):
        if not self.connected:
            await self.connect()
        try:
            payload = json.dumps(message).encode()
            await self.nc.publish(subject, payload)
            logger.info(f"[NATS] Published to {subject}: {message}")
        except Exception as e:
            logger.info(f"[NATS] Publish error: {e}")

    async def request(self, subject: str, message: dict, timeout=1.0):
        if not self.connected:
            await self.connect()
        try:
            payload = json.dumps(message).encode()
            msg = await self.nc.request(subject, payload, timeout=timeout)
            return json.loads(msg.data.decode())
        except ErrTimeout:
            logger.info("[NATS] Request timeout")
            return None
        except Exception as e:
            logger.info(f"[NATS] Request error: {e}")
            return None

    async def subscribe(self, subject: str, callback, queue: str):
        if not self.connected:
            await self.connect()
        await self.nc.subscribe(subject, cb=callback, queue=queue)

    async def close(self):
        if self.connected:
            await self.nc.drain()
            self.connected = False
            logger.info("[NATS] Connection closed")
