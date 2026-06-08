from __future__ import annotations

import sqlite3
import bcrypt
from pathlib import Path
from dataclasses import dataclass

@dataclass
class User:
    username: str
    is_admin: bool = False

class AuthService:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self._db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_widgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    dataset_key TEXT NOT NULL,
                    chart_type TEXT NOT NULL,
                    x_axis TEXT NOT NULL,
                    y_axis TEXT,
                    FOREIGN KEY(username) REFERENCES users(username)
                )
            """)
            conn.commit()

    def get_user_widgets(self, username: str) -> list[dict]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT dataset_key, chart_type, x_axis, y_axis, id FROM user_widgets WHERE username = ?",
                (username,)
            )
            return [
                {"dataset": row[0], "type": row[1], "x": row[2], "y": row[3], "id": row[4]}
                for row in cursor.fetchall()
            ]

    def add_user_widget(self, username: str, widget: dict) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO user_widgets (username, dataset_key, chart_type, x_axis, y_axis) VALUES (?, ?, ?, ?, ?)",
                (username, widget['dataset'], widget['type'], widget['x'], widget['y'])
            )
            conn.commit()
            return cursor.lastrowid

    def remove_user_widget(self, widget_id: int, username: str) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM user_widgets WHERE id = ? AND username = ?", (widget_id, username))
            conn.commit()

    def register_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                    (username, hashed, 1 if is_admin else 0)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> User | None:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT password_hash, is_admin FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            
            if row and bcrypt.checkpw(password.encode('utf-8'), row[0].encode('utf-8')):
                return User(username=username, is_admin=bool(row[1]))
        return None

    def change_password(self, username: str, new_password: str) -> bool:
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (hashed, username)
            )
            conn.commit()
            return True
