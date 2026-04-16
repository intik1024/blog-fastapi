# Blog API

REST API для блога с JWT аутентификацией, постами, комментариями и тегами.

## Технологии
- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT (python-jose)
- bcrypt (хеширование паролей)
- Pydantic

## Возможности
- Регистрация и логин (JWT токены)
- CRUD постов (только автор может редактировать)
- Комментарии к постам (с ответами)
- Теги для постов (связь многие-ко-многим)
- Пагинация, фильтрация

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/intik1024/blog-fastapi.git
cd blog-fastapi

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать базу данных PostgreSQL
# Создать БД blog_db

# 5. Создать файл .env
DATABASE_URL=postgresql://postgres:123@localhost/blog_db
SECRET_KEY=your-secret-key

# 6. Запустить миграции
# alembic upgrade head

# 7. Запустить сервер
uvicorn main:app --reload
