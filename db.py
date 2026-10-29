import sqlite3
from pathlib import Path

DB_DIR = Path("data")

def init_db():
    DB_DIR.mkdir(exist_ok=True)
    DB_PATH = Path(DB_DIR, "db.db")
    con = sqlite3.connect(DB_PATH, check_same_thread=False)

    with con:
        con.execute("PRAGMA journal_mode = WAL")

        query = """
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                post_time TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """
        con.execute(query)

        query2 = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                hashed_password TEXT NOT NULL
            );
        """
        con.execute(query2)
        con.commit()

    return con