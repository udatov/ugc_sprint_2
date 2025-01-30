# Сервис UGC

## Требования в сервису UGC
* Быстрая обработка входящих post реквестов от других сервисов.
* Внутрениий технический сервис, API не предназачен для прямой коммуникации с конечными пользователями,
* Задача сервиса сохранять действия пользователя, но не хранить постоянную информацию, такую как отзывы, рейтинги и т.п., что является задчей сервиса admin/search,
* Сбор и сохранение действий пользователя - для дальнейшего анализа:
    - История просмотров: какие фильмы просмотрены полностью, на какой секунде остановка,
    - Поиск: фильмов, персон, жанров,
    - Рейтинг: установка,
    - Отзывы: создание, удаление, изменение,
    - Избранное: добавление, удаление фильма.


## Важные эндпоинты:
* ugc/api/v1/{category}/{action}/ 

## Топики для Kafka
```json
favorite_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str"
    }

rating_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "score": "float"
    }

review_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "review_id": "str",
    "content": "str"
    }

watching_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "fully_watched": "bool",
    "stopped_at_time": "str"
    }

searching_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "query": "str",
    "search_by": "str"
    }

user_activity = {
    "user_id": "str",
    "category": "str",
    "action": "str",
    "details": {
        "user_id": "str",
        "film_id": "str",
        "action": "str"
    },
    "timestamp": "datetime"
    }

```

## В проекте используются следующие контейнеры
* ugc-backend
* ugc-kafka-0
* ugc-kafka-1
* ugc-kafka-2                                                                                                                                                                                                 
* ugc-kafka-ui-1
* nginx                                                                                                                                                                                                       1.5s 
* jaeger
