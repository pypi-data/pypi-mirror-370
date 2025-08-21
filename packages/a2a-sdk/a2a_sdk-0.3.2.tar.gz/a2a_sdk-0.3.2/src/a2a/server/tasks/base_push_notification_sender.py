import asyncio
import logging

import httpx

from a2a.server.tasks.push_notification_config_store import (
    PushNotificationConfigStore,
)
from a2a.server.tasks.push_notification_sender import PushNotificationSender
from a2a.types import PushNotificationConfig, Task


logger = logging.getLogger(__name__)


class BasePushNotificationSender(PushNotificationSender):
    """Base implementation of PushNotificationSender interface."""

    def __init__(
        self,
        httpx_client: httpx.AsyncClient,
        config_store: PushNotificationConfigStore,
    ) -> None:
        """Initializes the BasePushNotificationSender.

        Args:
            httpx_client: An async HTTP client instance to send notifications.
            config_store: A PushNotificationConfigStore instance to retrieve configurations.
        """
        self._client = httpx_client
        self._config_store = config_store

    async def send_notification(self, task: Task) -> None:
        """Sends a push notification for a task if configuration exists."""
        push_configs = await self._config_store.get_info(task.id)
        if not push_configs:
            return

        awaitables = [
            self._dispatch_notification(task, push_info)
            for push_info in push_configs
        ]
        results = await asyncio.gather(*awaitables)

        if not all(results):
            logger.warning(
                f'Some push notifications failed to send for task_id={task.id}'
            )

    async def _dispatch_notification(
        self, task: Task, push_info: PushNotificationConfig
    ) -> bool:
        url = push_info.url
        try:
            headers = None
            if push_info.token:
                headers = {'X-A2A-Notification-Token': push_info.token}
            response = await self._client.post(
                url,
                json=task.model_dump(mode='json', exclude_none=True),
                headers=headers,
            )
            response.raise_for_status()
            logger.info(
                f'Push-notification sent for task_id={task.id} to URL: {url}'
            )
        except Exception:
            logger.exception(
                f'Error sending push-notification for task_id={task.id} to URL: {url}.'
            )
            return False
        return True
