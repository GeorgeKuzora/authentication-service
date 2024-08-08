import logging

from fastapi import UploadFile

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Очередь сообщений kafka."""

    async def upload_image(self, username: str, image: UploadFile) -> None:
        """Функция для отправки сообщения в kafka."""
        data_uuid = username + str(image)  # заглушка
        logger.debug(data_uuid)
