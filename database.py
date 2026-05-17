# database.py — Gerenciamento do ranking SQLite

import sqlite3
from datetime import datetime
from config import DB_PATH, TOP_N


def init_db():
    """Cria tabela se não existir."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ranking (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                score     INTEGER NOT NULL,
                avatar    INTEGER DEFAULT 0,
                date      TEXT    NOT NULL
            )
        """)
        conn.commit()


def save_score(name: str, score: int, avatar: int = 0):
    """Salva uma partida no banco."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO ranking (name, score, avatar, date) VALUES (?, ?, ?, ?)",
            (name, score, avatar, datetime.now().strftime("%d/%m/%Y %H:%M"))
        )
        conn.commit()


def get_top(n: int = TOP_N) -> list[tuple]:
    """Retorna os top-N scores como lista de tuplas (name, score, date)."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name, score, date FROM ranking ORDER BY score DESC LIMIT ?", (n,)
        ).fetchall()
    return rows


def get_best_score() -> int:
    """Retorna o maior score já registrado."""
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT MAX(score) FROM ranking").fetchone()
    return row[0] if row and row[0] else 0
