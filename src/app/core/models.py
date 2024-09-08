import logging
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

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
    username_max_len=50,  # noqa: WPS 432 to avoid magic numbers
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

    def __eq__(self, object: Any) -> bool:  # noqa: WPS125, E501 magic method signature
        """
        Метод сравнения двух объектов.

        :param object: объект для сравнения
        :type object: Any
        :return: логическое значение равны ли объекты
        :rtype: bool
        """
        not_equal = False
        if not isinstance(self, self.__class__):
            return not_equal
        equal: bool = (
            self.username == object.username and
            self.password_hash == object.password_hash
        )
        return equal  # noqa: WPS331 MyPy suggestion


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

    def __eq__(self, object: Any) -> bool:  # noqa: WPS125, E501 magic method signature
        """
        Метод сравнения двух объектов.

        :param object: объект для сравнения
        :type object: Self
        :return: логическое значение равны ли объекты
        :rtype: bool
        """
        not_equal = False
        if not isinstance(self, self.__class__):
            return not_equal
        equal: bool = (
            self.subject == object.subject and
            self.issued_at == object.issued_at and
            self.encoded_token == object.encoded_token
        )
        return equal  # noqa: WPS331 MyPy suggestion

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
        max_length=validation_rules.password_max_len,
        min_length=validation_rules.password_min_len,
    )
