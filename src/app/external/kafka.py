import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from aiokafka import AIOKafkaProducer
from fastapi import UploadFile

from app.core.config.config import get_settings

logger = logging.getLogger(__name__)


class KafkaProducer:  # noqa: WPS214 for now 8 methods, will extract in future
    """Очередь сообщений kafka."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=get_settings().kafka.instance,
            value_serializer=self.serializer,
            compression_type='gzip',
        )
        self._init_storage_path()

    async def upload_image(self, username: str, image: UploadFile) -> None:
        """
        Функция для отправки изображения в kafka.

        Сохраняет изображение в файловую систему.
        Передает путь к файлу в сообщение kafka.

        :param username: Имя пользователя.
        :type username: str
        :param image: Изображение пользователя.
        :type image: UploadFile
        """
        file_path = self._get_unique_file_path(username)
        message = {
            'username': username,
            'file_path': file_path,
        }
        file_contents = await image.read()
        try:
            with open(file_path, 'wb') as image_file:
                image_file.write(file_contents)
                logger.info(f'{file_path} saved successfully')
        except Exception as file_err:
            logger.error(f'{file_path} not saved, {file_err.args}')
            return
        try:
            await self.producer.send_and_wait(
                get_settings().kafka.topics, message,
            )
        except Exception as kafka_err:
            logger.error(f'{message} not sent, {kafka_err.args}')
            return
        logger.info(f'{message} sent successfully')

    async def check_kafka(self) -> bool:
        """
        Проверяет что kafka доступна.

        Проверяет что kafka доступна,
        путем запроса метаданных клиента kafka.

        :return: True если kafka доступна, False в противном случае.
        :rtype: bool
        """
        try:
            await self.producer.client.fetch_all_metadata()
        except Exception as exc:
            logging.error(f'Kafka is not available: {exc}')
        else:
            return True
        return False

    def serializer(self, value: dict[str, str]) -> bytes:  # noqa: WPS110, E501 should be by docs
        """
        Сериализирует сообщение перед отправкой в kafka.

        :param value: Строковое представление сообщения.
        :type value: dict[str, str]
        :return: Сериализированное сообщение.
        :rtype: bytes
        """
        return json.dumps(value).encode()

    async def start(self) -> None:
        """Запускает producer."""
        while True:
            try:
                await self.producer.start()
            except Exception as exc:
                logger.warning('Waiting for Kafka to start:', exc_info=exc)
                await asyncio.sleep(10)
            else:
                break

    async def stop(self) -> None:
        """Останавливает producer."""
        await self.producer.stop()

    def _init_storage_path(self) -> None:
        path = Path(get_settings().kafka.storage_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise OSError(f'{path} is already exists and not a directory')

    def _get_unique_file_path(self, username) -> str:
        """Создает уникальный путь к файлу пользователя."""
        file_upload_timestamp = datetime.now().isoformat()
        filename = f'{username}-{file_upload_timestamp}'
        file_storage_path = get_settings().kafka.storage_path
        return f'{file_storage_path}/{filename}'
