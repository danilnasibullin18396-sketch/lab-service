# Сервис «Заметки» (Лаба 0)

Три части: **бэкенд** (Python/Flask), **фронтенд** (статическая страница), **БД** (PostgreSQL в Docker).

```
frontend (браузер) --HTTP/JSON--> backend (Flask, :5000) --SQL--> PostgreSQL (контейнер, :5432)
```

## API
- `GET  /api/notes`  — список заметок
- `POST /api/notes`  — добавить заметку, тело `{"text": "..."}`
- `GET  /api/health` — проверка живости (и БД)

## Запуск

### 1. База данных
Контейнер `lab-postgres` (образ `postgres:17-alpine`) должен быть запущен в Docker Desktop:
порт `5432`, том `pgdata`, `POSTGRES_USER=app`, `POSTGRES_DB=appd`.

### 2. Бэкенд (Windows, PowerShell)
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env     # откройте .env и впишите пароль от БД
python app.py
```
Проверка: http://localhost:5000/api/health → `{"status":"ok", ...}`

### 3. Фронтенд
В новом окне терминала в корневой папке проекта:
```powershell
python -m http.server 8080 -d ./frontend
```
Откройте http://localhost:8080

## Проверка работоспособности
1. Добавьте заметку через форму.
2. Перезагрузите страницу (F5): заметка на месте.
3. Убедитесь, что она лежит в БД:
```powershell
docker exec -it lab-postgres psql -U app -d appd -c "SELECT * FROM notes;"
```

## Настройки (переменные окружения / `.env`)
`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `PORT`, `INSTANCE_ID`.
