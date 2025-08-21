import json
import logging
from typing import Any

import aio_pika

logger = logging.getLogger(__name__)


async def send_messages(messages: list[dict[str, Any]], channel: aio_pika.Channel):
    if not messages:
        return

    for msg in messages:
        try:
            queue_name = msg["queue_name"]
            payload = json.dumps(msg["message"]).encode()

            await channel.default_exchange.publish(
                aio_pika.Message(body=payload, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue_name,
            )
            logger.info(f"Sent message to queue: {queue_name}")

        except Exception as e:
            logger.exception(f"Failed to send message to {msg.get('queue_name')}: {e}")
