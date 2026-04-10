# Letter Builder

Конструктор исходящих деловых писем для строительной компании.

## Стек

- **Backend:** Python 3.11 · FastAPI · SQLAlchemy async · PostgreSQL · Alembic · python-docx · LibreOffice headless
- **Frontend:** Vue 3 · TypeScript · Vite · Pinia · Tiptap · Pico CSS
- **Инфраструктура:** Docker Compose · Nginx

## Быстрый старт

```bash
cp .env.example .env
# Заполни DB_PASSWORD и SECRET_KEY в .env
docker compose up --build
```

Приложение доступно на http://localhost:3010

## Развёртывание на сервере

Nginx Proxy Manager → `letters.demo.corpcore.ru` → `localhost:3010`

## Функциональность

- Регистрация/авторизация (первый пользователь — автоматически admin)
- Управление организацией (реквизиты, лого, подпись)
- Проекты с адресатами
- Редактор писем (Tiptap rich text + live preview A4)
- Генерация DOCX/PDF с точным воспроизведением шаблона (шапка с лого, реквизиты, подпись)
- Автосохранение черновиков
- Управление пользователями (admin)

## Структура

```
letter-builder/
├── backend/       # FastAPI + python-docx
├── frontend/      # Vue 3 + Vite
└── docker-compose.yml
```
