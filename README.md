## Общее описание -- Проект обучения Middle Python Developer 
### Ссылка на текущий проект
https://github.com/udatov/ugc_sprint_2


## Особенности
Имею скромный опыт, выполняю проект в одиночку, чтобы в своём темпе глубже вникнуть в технологии.
Согласно ТЗ (для одиноких) часть задач не выполняю.

# Используемые технологии:
* Код Python + FastAPI + SQlAlchemy.
* Запуск на базе сервиса ASGI(uvicorn).
* В качестве хранилища Postgres, Elasticsearch.
* Кеширования Redis Cluster.
* Запуск через Docker Compose.

## Доступны следующие README.md
* [sprint9 - бекэнд likes (текущий проект)](./likes/README.md)
* [sprint8 - бекэнд ugc](./ugc/README.md)
* [sprint7 - бекэнд auth](./auth/README.md)


# Технические инструкции

## Кэширование
Для кеширования используем библиотеку `fastapi-cache2`

Для того, чтоб сделать ендпоинт кешируемым, нужно добавить декоратор `cache` к функции, которая его обрабатывает.

Пример:
```python
...

@router.get("/")
@cache(expire=120)
async def service():
    ...

```
  
## Pre-commit
Добавлен pre-commit. Если он установлен, то будет запускаться каждый раз при попытке сделать коммит в репозиторий. 
Для установки pre-commit необходимо выполнить следующие команды:
```bash 
pre-commit install
```
для удаления pre-commit: 
```bash
pre-commit uninstall
```
Если не хочется, чтобы выполнялись проверки при коммите, то можно не устанавливать pre-commit, но тогда просьба выполнять проверки перед коммитом самостоятельно.
Проверку можно запустить при помощи команды:
```bash
pre-commit run --all-files
```

В pre-commit используются следующие проверки:
* black - автоформатирование кода
* flake8 - проверка на соответствие pep8
* autoflake - удаление неиспользуемых импортов и переменных
* isort - сортировка импортов
* ruff - общий линтер

Для корректной работы библиотек black и isort нужно создать файл pyproject.toml в корне проекта и добавить в него следующие строки:
```toml
[tool.black]
line-length = 88
target-version = ['py311']
skip-magic-trailing-comma = 1

[tool.isort]
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
line_length = 88
```

## Requirements
Для установки всех необходимых библиотек при локальной отладке выполнить команду:
```bash
pip install -r requirements/dev.txt
```

Для релиза следует использовать файл requirements/prod.txt:
```bash
pip install -r requirements/prod.txt
```

## Запуск тестов
Установить зависимости:
```bash
pip install -r tests/requirements
```
Поднять тестовый docker-compose:
```bash
docker-compose -f tests/docker-compose.ymal up -d
``` 
Выполнить команду:
```bash
pytest test 
```

## Использование профилей docker compose
Основной файл docker-compose.yaml находится в корне проекта, в рамках данного файлы запускаются общие сервисы, например nginx, а также подключаются дополнительные файлы docker-compose.yaml соответствующих проектов, например:
```bash
include:
  - auth/docker-compose.yml   #name: sprint6
  - search/docker-compose.yml #name: sprint4
  - etl/docker-compose.yml    #name: sprint3
```

Станадртный запуск без профилей, с указанием конфигурационного файла 
```bash
docker-compose -f tests/docker-compose.ymal up -d
```

Для разделения запуска сервисов по проектам используются профили и шаблоны docker compose.
На текущий момент доступны следующие профили:
* **etl** - профиль ETL-процессов
* **search** - профиль для запуска сервиса API фильмов
* **auth** - профиль для запуска сервиса API пользователей и ролей

### Использование
Запуск, остановка конкретного профиля:
```bash
docker compose --profile search up -d
docker compose --profile search down
```

Запуск нескольких профилей
```bash
docker compose --profile search --profile auth up -d
docker compose --profile search --profile auth down
```

Чтобы не выбирать профили, можно указать переменную среды
```bash
export COMPOSE_PROFILES=search,auth,admin,etl
```

Запуск выделенного сервиса
```bash
docker compose run elasticsearch
```

Принудительное удаление контейнеров
```bash
docker ps -aq --filter name="sprint6*" | xargs docker stop | xargs docker rm --force
```

###Примечание
Если сервис не привязан ни к какому профилю, то он запускается при вызове любого профиля.

## Установка общая, применимо для любого проекта
```bash 
git clone https://github.com/udatov/Auth_sprint_1.git
docker-compose up -d
```

## Через браузер доступны

### Swagger FastAPI
* /api/openapi

### Сервисы
* /admin - административная панель Django для управления контентом, аутентификация чз сервис auth
* /api/v1 - центральная точка входа для сервиса поиска фильмов
* /auth/api/v1 - центральная точка входа сервиса авторизации


## Миграции Alembic
```bash 
alembic init .\db\migrations
alembic revision --autogenerate -m 'init'
alembic check
alembic upgrade head
```

## Настройки логирования 
В логгере настраивается логгирование uvicorn-сервера.
Про логирование в Python можно прочитать в документации
* https://docs.python.org/3/howto/logging.html
* https://docs.python.org/3/howto/logging-cookbook.html


## Создание супер пользователя
### Fast Api Auth backend
```bash 
python.exe -m utils.create_superuser
```