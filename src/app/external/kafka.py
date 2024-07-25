import logging

from fastapi import UploadFile

logger = logging.getLogger(__name__)


class KafkaQueue:
    """Очередь сообщений kafka."""

    async def send_message(self, username: str, image: UploadFile) -> None:
        """Функция для отправки сообщения в kafka."""
        data_uuid = user_id + str(image)  # заглушка
        logger.debug(data_uuid)
