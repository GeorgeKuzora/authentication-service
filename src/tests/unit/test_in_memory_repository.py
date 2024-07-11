import pytest

from app.in_memory_repository import Token, User
from tests.unit.conftest import invalid_user, token_list, user_list


class TestCreateUser:
    """Тестируем метод create_user."""

    @pytest.mark.parametrize(
        'user, expected, expected_user_id', (
            pytest.param(
                user_list[0], user_list[0], 0, id='get user in response',
            ),
            pytest.param(
                user_list[1], user_list[1], 0, id='get user in response',
            ),
        ),
    )
    def test_create_user_returns_indexed_user(
        self, user: User, expected: User, expected_user_id, repository,  # noqa
    ):
        """Тестирует что возвращается пользователь с верным id."""
        response_user: User = repository.create_user(user)

        assert response_user.username == expected.username
        assert response_user.user_id == expected_user_id

    @pytest.mark.parametrize(
        'user_list, expected_last_user_id', (
            pytest.param(user_list, 1, id='index increases'),
        ),
    )
    def test_create_user_db_index_increases(
        self, user_list: list[User], expected_last_user_id, repository,  # noqa
    ):
        """Тестирует что индекс при создании пользователя растет."""
        for user in user_list:
            response_user: User = repository.create_user(user)

        users_db_len = len(repository.users)

        assert response_user.user_id == expected_last_user_id
        # index starts at 0
        assert users_db_len == expected_last_user_id + 1


class TestCreateToken:
    """Тестирует метод create_token."""

    @pytest.mark.parametrize(
        'token, expected, expected_token_id', (
            pytest.param(
                token_list[0], token_list[0], 0, id='get token in response',
            ),
            pytest.param(
                token_list[1], token_list[1], 0, id='get token in response',
            ),
        ),
    )
    def test_create_token_returns_indexed_token(
        self, token: Token, expected: Token, expected_token_id, repository,  # noqa
    ):
        """Тестирует что возвращается токен с верным id."""
        response_token: Token = repository.create_token(token)

        assert response_token.encoded_token == expected.encoded_token
        assert response_token.token_id == expected_token_id

    @pytest.mark.parametrize(
        'token_list, expected_last_token_id', (
            pytest.param(token_list, 1, id='index increases'),
        ),
    )
    def test_create_token_db_index_increases(
        self, token_list: list[Token], expected_last_token_id, repository,  # noqa
    ):
        """Тестирует что индекс при создании токена получает инкремент."""
        for token in token_list:
            response_token: Token = repository.create_token(token)

        tokens_db_len = len(repository.tokens)

        assert response_token.token_id == expected_last_token_id
        # index starts at 0
        assert tokens_db_len == expected_last_token_id + 1


class TestGetUser:
    """Тестирует метод get_user."""

    @pytest.mark.parametrize(
        'user, repository_state_factory, expected_user', (
            pytest.param(
                user_list[0],
                'single_user_in_repo_facrory',
                user_list[0],
                id='first user in repo',
            ),
            pytest.param(
                user_list[1],
                'two_users_in_repo_facrory',
                user_list[1],
                id='second user in repo',
            ),
        ),
    )
    def test_get_user(
        self, user: User, repository_state_factory, expected_user, request,
    ):
        """Тетстирует получение пользователя."""
        repository, users_in_db = request.getfixturevalue(  # noqa
            repository_state_factory,
        )
        expected_user_id = users_in_db - 1

        respose_user: User | None = repository.get_user(user)

        if respose_user is None:
            raise AssertionError
        assert respose_user.username == expected_user.username
        assert respose_user.user_id == expected_user_id

    @pytest.mark.parametrize(
        'invalid_user, repository_state_factory, expected', (
            pytest.param(
                invalid_user,
                'two_users_in_repo_facrory',
                None,
                id='second user in repo',
            ),
        ),
    )
    def test_get_user_returns_none(
        self, invalid_user: User, repository_state_factory, expected, request,  # noqa
    ):
        """Тестирует что возвращен None если пользователь не найден."""
        repository, _ = request.getfixturevalue(  # noqa
            repository_state_factory,
        )

        respose_user: User | None = repository.get_user(invalid_user)

        assert respose_user == expected


class TestGetToken:
    """Тестирует метод get_token."""

    @pytest.mark.parametrize(
        'user, repository_state_factory, expected_token', (
            pytest.param(
                user_list[0],
                'single_token_in_repo_facrory',
                token_list[0],
                id='first token in repo',
            ),
            pytest.param(
                user_list[1],
                'two_tokens_in_repo_facrory',
                token_list[1],
                id='second token in repo',
            ),
        ),
    )
    def test_get_token(
        self, user: Token, repository_state_factory, expected_token, request,
    ):
        """Тетстирует получение токена."""
        repository, tokens_in_db = request.getfixturevalue(  # noqa
            repository_state_factory,
        )
        expected_token_id = tokens_in_db - 1
        respose_token: Token | None = repository.get_token(user)

        if respose_token is None:
            raise AssertionError
        assert respose_token.encoded_token == expected_token.encoded_token
        assert respose_token.token_id == expected_token_id

    @pytest.mark.parametrize(
        'invalid_token, repository_state_factory, expected', (
            pytest.param(
                invalid_user,
                'two_tokens_in_repo_facrory',
                None,
                id='second token in repo',
            ),
        ),
    )
    def test_get_token_returns_none(
        self,
        invalid_token: Token,
        repository_state_factory,
        expected,
        request,
    ):
        """Тестирует что возвращен None если токен не найден."""
        repository, _ = request.getfixturevalue(  # noqa
            repository_state_factory,
        )

        respose_token: Token | None = repository.get_token(invalid_token)

        assert respose_token == expected


@pytest.mark.parametrize(
    'token, repository_state_factory, expected_token, expected_id', (
        pytest.param(
            token_list[0],
            'single_token_in_repo_facrory',
            token_list[0],
            0,
            id='token found and updated',
        ),
        pytest.param(
            token_list[1],
            'single_token_in_repo_facrory',
            token_list[1],
            1,
            id='token not found and created',
        ),
    ),
)
def test_update_token(
    token, repository_state_factory, expected_token, expected_id, request,
):
    """Тетстирует обновление токена."""
    repository, _ = request.getfixturevalue(  # noqa
        repository_state_factory,
    )

    respose_token: Token = repository.update_token(token)

    if respose_token is None:
        raise AssertionError
    assert respose_token.encoded_token == expected_token.encoded_token
    assert respose_token.token_id == expected_id
