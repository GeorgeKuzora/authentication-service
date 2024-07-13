import logging

from app.config import get_auth_config
from app.in_memory_repository import InMemoryRepository
from app.service import AuthService

logger = logging.getLogger(__name__)


def main() -> None:
    """Устанавливает точку входа в программу."""
    repository = InMemoryRepository()
    config = get_auth_config()
    service = AuthService(repository, config)

    logger.info('user registration\n')
    token = service.register(
        username='jonny', password='password1',
    )
    logger.info(f'created {token}')

    logger.info('failed user authentication\n')
    token = service.authenticate(
        username='jonny', password='password2',
    )
    logger.info(f'created {token}')

    logger.info('user not found\n')
    token = service.authenticate(
        username='peter', password='password1',
    )
    logger.info(f'created {token}')

    logger.info('user authentication\n')
    token = service.authenticate(
        username='jonny', password='password1',
    )
    logger.info(f'created {token}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
