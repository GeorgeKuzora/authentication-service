import logging
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Self

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

ValidationRules = namedtuple(
    'ValidationRules',
    [
        'username_max_len',
        'password_max_len',
        'password_min_len',
    ],
)

validation_rules = ValidationRules(
    username_max_len=50,  # noqa: WPS 432 to avoid magic nambers
    password_max_len=100,
    password_min_len=8,
)


class User(BaseModel):
    """
    Данные о пользователе.

    Attributes:
        username: str - имя пользователя
        password_hash: str - хэш пароля пользователя
    """

    username: str
    password_hash: str
    user_id: int | None = None

    def __eq__(self, user: Self) -> bool:
        """
        Метод сравнения двух объектов.

        :param user: объект для сравнения
        :type: object
        :return: логическое значение равны ли объекты
        :rtype: bool
        :raises ValidationError: Если тип переданного значения не верен
        """
        if not isinstance(self, Self):
            user_type = type(user)
            logger.error(f'expected User but received {user_type}')
            raise ValidationError(f'expected User but received {user_type}')
        return (
            self.username == user.username and
            self.password_hash == user.password_hash
        )


class Token(BaseModel):
    """
    Данные о токене.

    Attributes:
        subject: User - пользовать для которого создан токен
        issued_at: datetime - дата и время создания токена
        encoded_token: str - кодированное представление токена
    """

    subject: str
    issued_at: datetime
    encoded_token: str
    token_id: int | None = None

    def __eq__(self, token: Self) -> bool:
        """
        Метод сравнения двух объектов.

        :param token: объект для сравнения
        :type: Self
        :return: логическое значение равны ли объекты
        :rtype: bool
        :raises ValidationError: Если тип переданного значения не верен
        """
        if not isinstance(self, Self):
            token_type = type(token)
            logger.error(f'expected Token but received {token_type}')
            raise ValidationError(f'expected Token but received {token_type}')
        return (
            self.subject == token.subject and
            self.issued_at == token.issued_at and
            self.encoded_token == token.encoded_token
        )

    def __str__(self) -> str:
        """Метод получения представления объекта в виде строки."""
        return f'{self.subject}, {self.issued_at}'

    def is_expired(self) -> bool:
        """Проверяет срок действия токена."""
        timedelta_config = {'days': 0, 'hours': 1, 'minutes': 0}
        return datetime.now() > self.issued_at + timedelta(**timedelta_config)


class UserCredentials(BaseModel):
    """Данные аутентификации пользователя."""

    username: str = Field(
        title='Имя пользователя',
        max_length=validation_rules.username_max_len,
    )
    password: str = Field(
        title='Пароль пользователя',
        max_length=validation_rules.username_max_len,
        min_length=validation_rules.password_min_len,
    )


