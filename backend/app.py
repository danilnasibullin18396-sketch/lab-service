import os
import socket
import time

import psycopg
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "app"),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", "appdb"),
}

INSTANCE_ID = os.getenv("INSTANCE_ID", socket.gethostname())

app = Flask(__name__)
CORS(app, expose_headers=["X-Instance-Id"])


@app.after_request
def add_instance_header(response):
    response.headers["X-Instance-Id"] = INSTANCE_ID
    return response


def get_conn():
    return psycopg.connect(**DB, connect_timeout=5)


def init_db(retries=10, delay=2):
    """Создаёт таблицу; повторяет попытки, пока БД не станет доступна."""
    for attempt in range(1, retries + 1):
        try:
            with get_conn() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS notes ("
                    "id SERIAL PRIMARY KEY, "
                    "text TEXT NOT NULL, "
                    "created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
                )
            return
        except psycopg.OperationalError as exc:
            print(f"БД недоступна (попытка {attempt}/{retries}): {exc}")
            time.sleep(delay)
    raise SystemExit("Не удалось подключиться к БД")


def note_to_dict(row):
    return {"id": row[0], "text": row[1], "created_at": row[2].isoformat()}


@app.get("/api/health")
def health():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        return jsonify(status="db_down", instance=INSTANCE_ID), 503
    return jsonify(status="ok", instance=INSTANCE_ID)


@app.get("/api/notes")
def list_notes():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return jsonify(instance=INSTANCE_ID, notes=[note_to_dict(r) for r in rows])


@app.post("/api/notes")
def add_note():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text or len(text) > 500:
        return jsonify(error="Текст заметки: от 1 до 500 символов"), 400
    with get_conn() as conn:
        row = conn.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id, text, created_at",
            (text,),
        ).fetchone()
    return jsonify(instance=INSTANCE_ID, note=note_to_dict(row)), 201


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
