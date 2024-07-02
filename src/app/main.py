import logging
import time

from app.in_memory_repository import InMemoryRepository
from app.service import AuthService

logger = logging.getLogger(__name__)


def main() -> None:
    """Устанавливает точку входа в программу."""
    repository = InMemoryRepository()
    service = AuthService(repository)

    logger.info('Регистрация пользователя\n')
    token = service.register(
        username='jonny', password='password1',
    )
    logger.info(f'Создан токен {token}')

    time.sleep(3)

    logger.info('Провальная аутентификация пользователя\n')
    token = service.authenticate(
        username='jonny', password='password2',
    )
    logger.info(f'Создан токен {token}')

    time.sleep(3)

    logger.info('Пользователь не найден\n')
    token = service.authenticate(
        username='peter', password='password1',
    )
    logger.info(f'Создан токен {token}')

    time.sleep(3)

    logger.info('Аутентификация пользователя\n')
    token = service.authenticate(
        username='jonny', password='password1',
    )
    logger.info(f'Создан токен {token}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
