import logging

from app.core.authentication import AuthService
from app.core.config import get_auth_config
from app.external.in_memory_repository import InMemoryRepository

logger = logging.getLogger(__name__)


def main() -> None:
    """Устанавливает точку входа в программу."""
    repository = InMemoryRepository()
    config = get_auth_config()
    service = AuthService(repository, config)

    logger.info('user registration\n')
    service.register(  # noqa: S106 test password
        username='jonny', password='password1',
    )

    logger.info('failed user authentication\n')
    service.authenticate(  # noqa: S106 test password
        username='jonny', password='password2',
    )

    logger.info('user not found\n')
    service.authenticate(  # noqa: S106 test password
        username='peter', password='password1',
    )

    logger.info('user authentication\n')
    service.authenticate(  # noqa: S106 test password
        username='jonny', password='password1',
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
