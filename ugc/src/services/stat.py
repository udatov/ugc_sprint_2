import json
from datetime import datetime
from functools import lru_cache
from uuid import UUID

from core.config import settings
from db.kafka import kafka_producer
from utils.backoff import backoff


class StatService:
    def __init__(self):
        self.producer = kafka_producer

    @backoff()
    async def _send_to_kafka(self, topic: str, event: dict, key: str):
        """
        Internal method to send an event to a Kafka topic.

        :param topic: The Kafka topic to which the event will be sent.
        :param event: The event data to be sent.
        :param key: The key associated with the event for partitioning.
        """
        try:
            await self.producer.send(
                topic=topic,
                value=json.dumps(event).encode("utf-8"),
                key=key.encode("utf-8"),
            )
        except Exception as e:
            print(f"Error sending event to Kafka '{topic}': {e}")

    async def log_event(
        self, topic: str, user_id: str, action: str, category: str, **kwargs
    ):
        """
        General method to log an event to the specified Kafka topic.

        The method constructs an event with the user ID, action, category,
        and additional keyword arguments, and sends it to the Kafka topic.

        :param topic: Kafka topic to send the event to.
        :param user_id: User ID (or "anonymous" for anonymous actions).
        :param action: Specific action being logged (e.g., "add", "remove").
        :param kwargs: Additional details for the event payload.
        """
        event = {
            "user_id": str(user_id),
            "category": category,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            **kwargs,
        }
        key = f"{category}_{action}"
        await self._send_to_kafka(topic, event, key)

    async def log_user_activity(
        self, user_id: UUID, category: str, action: str, details: dict
    ):
        """
        Logs user activity to the `user_activity` topic.

        This method creates an event containing user activity details (user ID,
        category, action, and details) and sends it to the user activity topic.

        :param user_id: The ID of the user whose activity is being logged.
        :param category: Category of the user activity.
        :param action: Specific action performed by the user.
        :param details: Additional details related to the user activity.
        """
        event = {
            "user_id": str(user_id),
            "category": category,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        key = f"{category}_{action}"
        await self._send_to_kafka(settings.USER_ACTIVITY_topic, event, key)


@lru_cache()
def get_statistic_service() -> StatService:
    """
    Returns a singleton instance of StatService.
    """
    return StatService()
