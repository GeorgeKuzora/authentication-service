import logging

import brotli
from aiokafka import AIOKafkaProducer
from fastapi import UploadFile

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def create_producer() -> AIOKafkaProducer:
    """
    Создает AIOKafkaProducer.

    :return: экземпляр AIOKafkaProducer
    :rtype: AIOKafkaProducer
    """
    return AIOKafkaProducer(
        bootstrap_servers=get_settings().kafka.instance,
    )


producer = create_producer()


class KafkaProducer:
    """Очередь сообщений kafka."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.producer = producer

    async def upload_image(self, username: str, image: UploadFile) -> None:
        """Функция для отправки изображения в kafka."""
        data_uuid = username + str(image)  # заглушка
        logger.debug(data_uuid)
        file_path = f'/usr/photos/{image.filename}'
        try:
            with open(file_path, 'wb') as image_file:
                image_file.write(image.file.read())
                await producer.send_and_wait(
                    'faces', await self._compress(file_path),
                )
                logger.info('File saved successfully')
        except Exception as err:
            logger.error(f'File not saved, {err.args}')

    async def _compress(self, message: str) -> bytes:
        """
        Сжимаеш сообщение перед отправкой в kafra.

        :param message: Строковое представление сообщения.
        :type message: str
        :return: Сжатое изображение.
        :rtype: bytes
        """
        return brotli.compress(
            bytes(message, get_settings().kafka.file_encoding),
            quality=get_settings().kafka.file_compression_quality,
        )


async def check_kafka() -> bool:
    """
    Checks if Kafka is available by fetching all metadata from the Kafka client.

    :return: True if Kafka is available, False otherwise.
    :rtype: bool
    """
    try:
        await producer.client.fetch_all_metadata()
    except Exception as exc:
        logging.error(f'Kafka is not available: {exc}')
    else:
        return True
    return False
