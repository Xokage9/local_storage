<div align="center">

# Файловое хранилище

### Файлы, доступ и правила хранения

Учебное веб-приложение с серверной частью на FastAPI и интерфейсом на React.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Keycloak](https://img.shields.io/badge/Keycloak-2C2C2C?style=flat-square&logo=keycloak&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

</div>

## Возможности

| Область | Что реализовано |
|---|---|
| Хранилища | Создание хранилищ, участники и их роли |
| Файлы | Загрузка, потоковое скачивание, переименование, перенос и удаление |
| Папки | Организация файлов по папкам и поиск |
| Доступ | Роли участников, отдельные разрешения на файлы и ссылки доступа |
| Политики | Квоты хранилища, максимальный размер, расширения и MIME-типы |
| Аудит | Регистрация действий с файлами и доступом |
| Вход | Интеграция с Keycloak и проверка JWT |

## Устройство

| Часть | Ответственность | Где смотреть |
|---|---|---|
| API | HTTP-маршруты и зависимости | [backend/app/api](backend/app/api) |
| Сервисы | Доступ, файлы, квоты и журнал | [backend/app/services](backend/app/services) |
| Данные | SQLAlchemy-модели, репозитории и Alembic | [backend/app/models](backend/app/models), [миграции](backend/app/db/migrations) |
| Интеграции | Keycloak и локальная файловая система | [auth](backend/app/auth), [integrations](backend/app/integrations) |
| Интерфейс | React и TypeScript | [frontend/src](frontend/src) |

Метаданные хранятся в PostgreSQL, содержимое файлов — на локальном диске. Токены проверяются серверной частью; операции проходят через проверки доступа и сервисы предметной логики.

## Проверки

В [backend/tests](backend/tests) находятся тесты аутентификации, прав доступа, файлов, папок, хранилищ, квот и ссылок.

## Конфигурация

[Docker Compose](docker-compose.yml) описывает frontend, backend, PostgreSQL и Keycloak. Настройки backend: `DATABASE_URL`, `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `FILE_STORAGE_PATH` и `CORS_ORIGINS`. Параметры разработки и realm находятся в конфигурационных файлах проекта.
