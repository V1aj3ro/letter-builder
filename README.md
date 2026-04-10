# Letter Builder

Конструктор исходящих деловых писем.

## Стек

- **Backend:** Python 3.11 · FastAPI · SQLAlchemy async · PostgreSQL · Alembic · python-docx · LibreOffice headless
- **Frontend:** Vue 3 · TypeScript · Vite · Pinia · Tiptap · Pico CSS
- **Инфраструктура:** Docker Compose · Nginx


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
