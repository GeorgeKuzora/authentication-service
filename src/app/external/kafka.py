import logging
import json
from datetime import datetime
from pathlib import Path

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
        self._init_storage_path()

    async def upload_image(self, username: str, image: UploadFile) -> None:
        """Функция для отправки изображения в kafka."""
        file_path = self._get_file_path(username)
        message = {
            'username': username,
            'file_path': file_path,
        }
        try:
            with open(file_path, 'wb') as image_file:
                image_file.write(image.file.read())
                logger.info(f'{file_path} saved successfully')
        except Exception as file_err:
            logger.error(f'{file_path} not saved, {file_err.args}')
        try:
            await producer.send_and_wait(
                'faces', await self._compress(message),
            )
        except Exception as kafka_err:
            logger.error(f'{message} not sent, {kafka_err.args}')
        logger.info(f'{message} sent successfully')

    def _init_storage_path(self) -> None:
        path = Path(get_settings().kafka.storage_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise OSError(f'{path} is already exists and not a directory')

    def _get_file_path(self, username) -> str:
        """Создает уникальный путь к файлу пользователя."""
        file_upload_timestamp = datetime.now().isoformat()
        filename = f'{username}-{file_upload_timestamp}'
        file_storage_path = get_settings().kafka.storage_path
        return f'{file_storage_path}/{filename}'

    async def _compress(self, message: dict[str, str]) -> bytes:
        """
        Сериализирует сообщение перед отправкой в kafra.

        :param message: Строковое представление сообщения.
        :type message: dict[str, str]
        :return: Сериализованное сообщение.
        :rtype: bytes
        """
        return json.dumps(message).encode()


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
