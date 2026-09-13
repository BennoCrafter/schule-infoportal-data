import datetime
import os
import sqlite3
from pathlib import Path

import dotenv
import requests
from requests.auth import HTTPBasicAuth

from src.models import News, Substitution

dotenv.load_dotenv()
login_username = os.getenv("LOGIN_USERNAME", "")
login_password = os.getenv("PASSWORD", "")

BASE_URL = "https://schule-infoportal-api.vercel.app/"
DATA_DIR = os.getenv("DATA_DIR", "./data")
DB_PATH = Path(DATA_DIR) / "app_data.db"


class SubstitutionStorage:
    @staticmethod
    def _get_connection() -> sqlite3.Connection:
        os.makedirs(DATA_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Creates tables matching the Pydantic schemas."""
        with cls._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS substitutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL,
                    period TEXT NOT NULL,
                    absent_teacher TEXT NOT NULL,
                    substitution_teacher TEXT,
                    subject_abbreviation TEXT NOT NULL,
                    room TEXT NOT NULL,
                    info TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            """)
            conn.commit()

    @staticmethod
    def update():
        new_substitutions_batch, new_news_batch = (
            SubstitutionStorage.fetch_data_for_today()
        )

        SubstitutionStorage.write_to_disk(new_substitutions_batch, new_news_batch)

    @classmethod
    def write_to_disk(cls, substitutions: list[Substitution], news: list[News]):
        cls.init_db()

        with cls._get_connection() as conn:
            if substitutions:
                sub_records = [
                    (
                        sub.class_name,
                        sub.period,
                        sub.absent_teacher,
                        sub.substitution_teacher,
                        sub.subject_abbreviation,
                        sub.room,
                        sub.info,
                        sub.date.isoformat(),
                    )
                    for sub in substitutions
                ]
                conn.executemany(
                    """
                    INSERT INTO substitutions
                    (class_name, period, absent_teacher, substitution_teacher, subject_abbreviation, room, info, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    sub_records,
                )

            if news:
                news_records = [(n.message, n.date.isoformat()) for n in news]
                conn.executemany(
                    "INSERT INTO news (message, date) VALUES (?, ?)",
                    news_records,
                )

            conn.commit()

    @classmethod
    def read_substitutions(cls) -> list[Substitution]:
        """Queries substitutions and maps them directly back to Pydantic objects."""
        cls.init_db()
        with cls._get_connection() as conn:
            cursor = conn.execute(
                "SELECT class_name, period, absent_teacher, substitution_teacher, subject_abbreviation, room, info, date FROM substitutions"
            )
            return [Substitution(**dict(row)) for row in cursor.fetchall()]

    @classmethod
    def read_news(cls) -> list[News]:
        """Queries news and maps them directly back to Pydantic objects."""
        cls.init_db()
        with cls._get_connection() as conn:
            cursor = conn.execute("SELECT message, date FROM news")
            return [News(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def fetch_data_for_today() -> tuple[list[Substitution], list[News]]:
        substitutions = requests.get(
            BASE_URL
            + f"substitutions?date={datetime.date.today().strftime('%Y-%m-%d')}",
            auth=HTTPBasicAuth(login_username, login_password),
        ).json()

        news = requests.get(
            BASE_URL + "news/today",
            auth=HTTPBasicAuth(login_username, login_password),
        ).json()

        return [Substitution(**sub) for sub in substitutions], [News(**n) for n in news]
