## Важные эндпоинты:

* auth/api/v1/user/signin/ - Регистрация пользователя
* auth/api/v1/oauth/yandex/ - Использование Yandex аутентификации для полечения Yandex access token
* auth/api/v1/user/signin/ - Логин и получение access и refresh токенов, использовать либо логин\пароль либо Yandex access token

## Особенности
Имею скромный опыт, выполняю проект в одиночку, чтобы в своём темпе глубже вникнуть в технологии.

## Основные сущности
* User — id, login, first_name, last_name, created_at, is_superus
* Role — id, name, created_at

## В проекте используются следующие контейнеры
* `auth-backend` - непосредственно [код текущего спринта](./src)
* `auth-redis` - контейнер с Redis
* `auth-postgres` - база данных PostgreSQL
* `nginx` - балансировщик.
* `jaeger` - сборщик трейсов.
