
from descartcan.utils.log import logger


class EventRouter:
    def __init__(self):
        self.routes = {}

    def on(self, subject, queue=None):
        def decorator(func):
            self.routes[subject] = {"handler": func, "queue": queue}
            return func
        return decorator

    async def register(self, nats_client):
        for subject, meta in self.routes.items():
            async def handler(msg, func=meta["handler"]):
                await func(msg, nats_cli=nats_client)
            await nats_client.subscribe(subject, handler, meta["queue"])
            logger.info(f"[Router] Bound {meta['handler'].__name__} to '{subject}'")


event_router = EventRouter()

