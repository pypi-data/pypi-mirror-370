import sqlite3
import bcrypt
from functools import wraps
from flask import request, abort, Response
import time
import os
import atexit
import sys
from aicard.card import ModelCard

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

class UserDB:
    def __init__(self, logger, root:str="db", admin_name:str="admin", admin_password:str="admin", admin_email:str=""):
        if not root:
            logger.info("Initializing non-persistent testing database")
            conn = sqlite3.connect(":memory:", check_same_thread=True)
        else:
            os.makedirs(root, exist_ok=True)
            conn = sqlite3.connect(os.path.join(root, "auth.db"), check_same_thread=True)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode=WAL;")

        # create user tables
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS pending_users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )''')

        # create model card table
        prototype = ModelCard()
        col_names = list(prototype.data.flatten().keys())
        assert "user" not in col_names and "id" not in col_names and "desc" not in col_names, \
            "The ModelCard schema cannot be defined to include id, user, or desc fields at the top level, since these are externally managed by the service database"
        col_defs = ",\n    ".join([f'"{col}" TEXT' for col in col_names])
        create_cards_table = f'''CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            desc TEXT NOT NULL,
            {col_defs},
            FOREIGN KEY(user) REFERENCES users(username) ON DELETE CASCADE
        )'''
        conn.execute(create_cards_table)

        # automatic migration if needed
        expected_columns = ['id', 'user', 'desc'] + col_names
        cursor = conn.execute("PRAGMA table_info(cards)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        missing = [col for col in expected_columns if col not in existing_columns]
        redundant = [col for col in existing_columns if col not in expected_columns]

        if missing or redundant:
            logger.warn("The prototype for ModelCard does not match the database schema of cards. Migrating...")
            if missing:
                logger.warn(f"Adding missing columns: {', '.join(missing)}")
                for col in missing:
                    conn.execute(f'ALTER TABLE cards ADD COLUMN "{col}" TEXT')
            if redundant:
                logger.warn(f"The following columns are leftover and will be removed: {', '.join(redundant)}")
                print("To proceed with removing leftover columns, type 'migrate' and press Enter. Otherwise delete the database file")
                user_input = input(">> ").strip().lower()
                if user_input != "migrate":
                    logger.error("Migration cancelled. Please review the ModelCard schema schema.")
                    sys.exit(1)
                # SQLite doesn't support DROP COLUMN directly. So we recreate the table:
                temp_cols = [col for col in existing_columns if col not in redundant]
                temp_col_str = ', '.join([f'"{col}"' for col in temp_cols])
                conn.execute("BEGIN")
                conn.execute(f'CREATE TABLE cards_new AS SELECT {temp_col_str} FROM cards')
                conn.execute('DROP TABLE cards')
                conn.execute(create_cards_table)
                insert_cols = ', '.join(temp_cols)
                select_cols = ', '.join(temp_cols)
                conn.execute(f'INSERT INTO cards ({insert_cols}) SELECT {select_cols} FROM cards_new')
                conn.execute('DROP TABLE cards_new')
                conn.commit()
            else: logger.info("There are no leftover columns to be removed")

        conn.commit()
        atexit.register(conn.close)
        self.conn = conn
        if not self.find_user("users", admin_name):
            self.insert_user("users", admin_name, admin_email, admin_password)
            logger.info("First time run detected.")
            logger.ok(f"Created database and administrator user with default credentials.\n * name: {admin_name}\n * password: {admin_password}")
            logger.warn("REMEMBER TO CHANGE THE DEFAULT ADMINISTRATOR PASSWORD")
        else: logger.ok("Database loaded.")

    def find_user(self, table: str, username: str):
        cursor = self.conn.execute(
            f"SELECT username, email, password FROM {table} WHERE username = ?",
            (username,)
        )
        return cursor.fetchone()

    def insert_user(self, table_name: str, username: str, email: str, password: str, commit: bool=True):
        self.conn.execute(
            f"INSERT INTO {table_name} (username, email, password) VALUES (?, ?, ?)",
            (username, email, hash_password(password))
        )
        if commit: self.conn.commit()

def require_auth(token2expiration: dict):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "): abort(401, description="Missing token")
            parts = auth.strip().split()
            if len(parts) != 2 or parts[0] != "Bearer": abort(401, description="Invalid token format")
            token = parts[1]
            expiry = token2expiration.get(token)
            if not expiry or time.time() > expiry: abort(403, description="Token expired or invalid - please log in")
            return f(*args, **kwargs, token=token)
        return wrapper
    return decorator

def require_admin(token2expiration: dict):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth or not isinstance(auth, str): abort(401, description="Invalid token format")
            parts = auth.strip().split()
            if len(parts) != 2 or parts[0] != "Bearer": abort(403, description="Token expired or invalid - please log in")
            token = parts[1]
            expiry = token2expiration.get(token)
            if not expiry or time.time() > expiry: abort(403, description="Token expired or invalid - please log in")
            return f(*args, **kwargs, token=token)
        return wrapper
    return decorator
