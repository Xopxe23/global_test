# FastAPI app for Global


## В приложении реализованы следующие концепции:
- Разработка Веб-Приложений на Python[FastApi], следуя дизайну REST API.
- Подход Чистой Архитектуры в построении структуры приложения. Техника внедрения зависимости.
- Работа с БД Postgres. Генерация файлов миграций. 
- Работа с БД Redis и Celery. Отложенная отправка писем на email для верификации. 
- Работа с БД, используя библиотеку alembic
- Регистрация и аутентификация. Работа с JWT. Middleware

### Для подготовки окружения:
- Запущенный PostgreSQL (Создать пользователя и БД по типу .env)
- Запущенный Redis

### Для запуска приложения:

##### Устанавливаем зависимости

###### Для Mac/Linux
```
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

###### Для Windows
```
python3 -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
```

##### Выполняем миграции
```
alembic upgrade head
```

##### Запускаем приложение

```
python3 app/main.py  
```

##### Запускаем Celery
```
celery -A app.tasks.tasks.celery  worker -l INFO
```