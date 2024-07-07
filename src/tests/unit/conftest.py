from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.service import AuthService, RepositoryError, Token, User

issued_at = datetime.now()
encoded_token = 'sdfa.asfsd.safd'
user_list = [
    User('peter', '13rasf', 1),
    User('max', 'sdfad', 2),
]
token_list = [
    Token(user_list[0], issued_at, encoded_token, 1),
    Token(user_list[1], issued_at, encoded_token, 2),
]
