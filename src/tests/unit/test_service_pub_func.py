import pytest

from app.service import AuthService, RepositoryError, User
from tests.unit.conftest import raise_repository_error, token_list, user_list
