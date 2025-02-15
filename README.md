# Authentication Service

Репозиторий с сервисом для проведения регистрации и аутентификации пользователя.

От приложения ожидается использование [8080 порта](./.devcontainer/docker-compose.yml#L12) внутри контейнера.
На локальном хосте приложение будет доступно на [28080 порту](./.devcontainer/docker-compose.yml#L12).

## Описание сервиса

Сервис принимает HTTP запросы через следующий API:

- `/register` - Регистрация пользователя.
- `/login` - Аутентификация пользователя.
- `/check_token` - Проверка токена авторизации пользователя.
- `/verify` - Верификация пользователя по фотографии.

Приняв запрос сервис производит его обработку и сохраняет результаты в постоянном хранилище данных или в кэше:

- Данные о пользователе сохраняются в постоянном хранилище данных.
- Данные о токене пользователя сохраняются в кэше.

При выполнении верификации пользователя, сервис сохраняет полученное изображение в файловой системе. Затем сервис передает путь к изображению и имя пользователя в брокер сообщений kafka.

## Особенности

- Для доступа к функциям сервиса используется API на базе HTTP запросов.
- Для хранения данных сервис использует базу данных [PostgreSQL](https://www.postgresql.org/).
- Для кэширования данных используется [Redis](https://redis.io/)
- Настроена сборка приложения в Docker контейнере.
- Созданы манифесты для развертывания приложения в kubernetes.
- Созданы чарты helm для запуска и обновления сервиса в окружении kubernetes.
- Созданы метрики Prometheus.
- Добавлена трассировка запросов при помощи Jaeger.

## Используемые инструменты и технологии

- Python 3.12
- Fast API
- Pydantic
- Linux
- Docker
- PostgreSQL
- Redis
- Kubernetes
- Helm
- Kafka
- Prometheus
- Jaeger

## Локальная разработка и тестирование проекта

Проект разрабатывается в devcontainer. Информацию о том, как запустить проект и работать над ним, можно найти в файле [CONTRIBUTING.md](./CONTRIBUTING.md).
