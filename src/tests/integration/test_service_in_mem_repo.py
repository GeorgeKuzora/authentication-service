import pytest

from app.config import get_auth_config
from app.in_memory_repository import InMemoryRepository
from app.service import AuthService, Token, User
