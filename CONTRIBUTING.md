# Разработка и запуск проекта

Для разработки проекта используется рабочее окружение настроенное внутри devcontainer.

## Требования для разработки проекта в Devcontainer

В зависимости от используемой операционной системы некоторые шаги и команды могут отличаться. В этом случае обращайтесь к версии документации для вашей операционной системы.

Для работы над проектом в devcontainer необходимо:

- Для Windows: рекомендуется использовать [WSL](https://virgo.ftc.ru/pages/viewpage.action?pageId=1084887269).
- Установить Docker Desktop для MacOS/Windows или просто docker для Linux. [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- Установить [Visual Studio Code](https://code.visualstudio.com/download).
-  [Настроить Visual Studio Code и Docker для использования Devcontainers](https://code.visualstudio.com/docs/devcontainers/containers#_getting-started).
  - Необходимые плагины VS Code:
    - `ms-vscode-remote.remote-containers`
    - `ms-azuretools.vscode-docker`
- Установить Git
- Установить OpenSSH с SSH Agent.
- [Настроить Git и SSH для работы в Devcontainer](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
- Установить OpenSSL
- Установить [Шрифты для powerlevel10k](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#fonts)
- [Установить шрифт Meslo Nerd Font для CLI в терминале](https://github.com/romkatv/powerlevel10k?tab=readme-ov-file#fonts)
- По необходимости установить и настроить kubectl, внутри контейнера будут использованы настройки с хоста
- Клонировать этот репозиторий на рабочую станцию
- Открыть директорию с репозиторием через Visual Studio Code
- Ввести `Ctrl+Shift+P` или `Cmd+Shift+P` и выбрать `Dev Containers: Rebuild and Reopen in Container`

## Работа над проектом внутри Devcontainer

### Конфигурация рабочего окружения

Если какие-то из дальнейших пунктов у вас уже выполнены, смело пропускайте шаг.

После установки необходимого ПО:
- Сгенерируйте SSH ключ и добавьте его в свой MosHub аккаунт
- Настройте `user.name` и `user.email` для Git
- [Настройте SSH Agent c вашим ключом](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
- Клонируйте текущий репозиторий в локальную директорию, если еще не сделали этого

Для настройки kubernetes:
- Сгенерируйте ключи для kubectl и положите их в папку `~/.kube`
- Настройте kubectl на использование ключей из папки `~/.kube`

После настройки локального окружения:
- Откройте директорию в Visual Studio Code
- Нажмите `Ctrl+Shift+P` или `Cmd+Shift+P`
- Введите `Dev Containers:`
- Выберите из предложенных вариантов пункт `Dev Containers: Rebuild and Reopen in Container`
- Дождитесь открытия проекта внутри окружения в Devcontainer

### Окружение доступное после старта Devcontainer

После старта контейнера будут доступны следующие преднастроенные возможности:

#### Преднастроенная конфигурация для запуска линтера

  Доступ из командной панели:

  - Нажмите `Ctrl+Shift+P` или `Cmd+Shift+P`
  - Выберете `Tasks: Run Task`
  - Выберете `Flake8` или `ISort`

#### Преднастроенная конфигурация для запуска тестов

Смотрите по кнопке `Testing` в боковой панели Visual Studio Code.

#### Преднастроенная конфигурация для запуска сервиса

Смотрите по кнопке `Run and Debug` в боковой панели Visual Studio Code.

- `Zsh` с Oh-My-Zsh в качестве shell по-умолчанию
- базовые консольные инструменты вроде `git`, `curl` и прочие
- `kubectl` и `helm` для работы с kubernetes
- `python` версии 3.12 с `poetry` для управления зависимостями и виртуальным окружением
- настроен доступ до `docker` на хосте

### Файл .devcontainer/app/secrets

Файл `.devcontainer/app/secrets` служит для хранения секретного ключа и названия алгоритма кодирования JWT токена.

Для того чтобы контейнер собрался, этот файл добавлен в репозиторий но содержит данные по умолчанию. Их не следует использовать в иных случаях кроме разработки и тестирования.

Файл имеет формат переменных окружения. В нем определены две переменные:

- `SECRET_KEY` - секретный ключ в формате hex.
- `TOKEN_ALGORITHM` - алгоритм кодирования токена. По умолчанию `HS256`.

Для генерации своего секретного ключа можно использовать команду:

```shell
openssl rand -hex 32
```

Для передачи файла secrets используется элемент верхнего уровня `secrets` в файле `docker-compose.yml`. При сборке контейнера этот файл копируется в файл `/run/secrets/jwt_secrets`. Для доступа к переменным в файле используется библиотека `dotenv`.

### Работа с базой данных при работе в Devcontainer

#### Сервис db

Для работы с базой данных при работе в devcontainer при разработке и тестировании приложения, в docker-compose devcontainer добавлен сервис `db`.

Сервис `db` запускается совместно с devcontainer и доступен по dns-имени `db` на порту `5432`.

Данные авторизации сервиса `db` соответствуют данным размещенным в файле конфигурации `config-local.yml` и могут использоваться при локальной разработке, но не должны использоваться в продакшене.

#### Миграция базы данных

При начале работы с проектом. Или после изменений схемы базы данных в проекте необходимо выполнить миграцию базы данных. Миграция базы данных производится при помощи инструмента для управления миграциями `alembic`. `alembic` добавлен в зависимости проекта и устанавливается при старте dev-контейнера.

Для выполнения миграции базы данных необходимо убедиться, что совместно с dev-контейнером запущен сервис `db`. Для этого можно воспользоваться командой:

```shell
docker container list
```

В выводе команды должен быть работающий контейнер с сервисом `db`:

```
18bbf11d123a postgres:16.3 "docker-entrypoint.s…" 16 hours ago Up 16 hours 0.0.0.0:5432->5432/tcp, :::5432->5432/tcp face-verification-service_devcontainer-db-1
```

Затем необходимо применить существующие миграции проекта к базе данных. Для этого нужно выполнить команду:

```shell
alembic upgrade head
```

Если при выполнении команды не возникло ошибок, то база данных будет готова к работе.

#### Создание миграций

Если при работе над проектом вносятся изменения в схему базы данных. То эти изменения нужно добавить в файлы миграции alembic. Для этого следует воспользоваться следующей командой:

```shell
alembic revision --autogenerate -m "<Описание миграции>"
```

При этом `alembic` создает новый файл миграции в директории `alembic/versions/` где будут отражены изменения схеме базы данных если они были внесены через `sqlalchemy.orm`.

## Структура проекта

`.dockerignore` — файл для игнорирования файлов и директорий в ходе сборки Docker контейнера.
`.gitignore` - файл для игнорирования файлов и директорий в git.
`.gitlab-ci.yml` - файл пайплайна gitlab ci-cd.
`alembic-compose.ini` - файл конфигурации alembic в окружении docker-compose.
`alembic-kube.ini` - файл конфигурации alembic в окружении kubernetes.
`alembic.ini` - файл конфигурации alembic в локальном окружении.
`CHANGELOG.md` — файл изменений, содержащий информацию об изменениях в проекте.
`CONTRIBUTING.md` — файл с инструкциями по внесению вклада в проект.
`Dockerfile` — файл для создания образа Docker контейнера.
`poetry.lock` — файл блокировки зависимостей, который гарантирует, что все зависимости проекта будут одинаковыми на всех машинах разработчиков.
`pyproject.toml` — файл конфигурации Poetry, менеджера зависимостей для Python.
`setup.cfg` - файл конфигурации инструментов разработчика.
`README.md` — файл с описанием проекта.
`alembic/` - директория менеджера миграций alembic.
`helm/` - директория чартов helm.
`manifests/` - директория манифестов kubernetes.
`src/` — каталог с исходным кодом проекта.
`app/` — каталог с кодом сервиса.
`config/` — каталог с конфигурационными файлами проекта.
`tests/` — каталог с тестами проекта.

## Запуск приложения в Docker контейнере

Для приложения создан [Dockerfile](./Dockerfile).

Для запуска приложения в Docker контейнере необходимо:

Установить Docker Desktop для MacOS/Windows или просто docker для Linux. [Docker Desktop](https://www.docker.com/products/docker-desktop/).

При ручной сборке контейнера ожидается наличие файла секретов в проекте - `/app/src/config/secrets`.

Выполнить команду `docker build` для сборки образа контейнера:

```shell
docker build -t auth-service:latest .
```

Для создания и запуска контейнера выполните команду `docker run`:

```shell
docker run --name auth-service -p 127.0.0.1:8083:8000 auth-service
```

Приложение будет доступно на порту `127.0.0.1:8083`.

## Запуск сервиса в kubernetes

Для работы приложения в kubernetes созданы манифесты ресурсов kubernetes - `manifests`.

Для того чтобы запустить необходимые ресурсы в кластере kubernetes выполните следующие команды:

```shell
kubectl apply -f manifests/pvc.yml
kubectl apply -f manifests/configMap.yml
kubectl apply -f manifests/serivce.yml
kubectl apply -f manifests/deployment.yml
kubectl apply -f manifests/job.yml
```

Для упрощения работы с манифестами kubernetes создан пакет чартов helm. Для установки приложения в kubernetes при помощи helm выполните команду:

```shell
helm install kuzora-auth ./kuzora-auth
```
