import os
import sqlite3
import hashlib
from unittest import result


class DatabaseManager:
    def __init__(self, db_name="finance.db"):
        # Safe folder on desktop
        base_dir = os.path.join(os.environ["USERPROFILE"], "Desktop", "CashCaptainDB")
        os.makedirs(base_dir, exist_ok=True)
        db_path = os.path.join(base_dir, db_name)
        print("DB PATH:", db_path)

        try:
            # Connect to database (auto-creates if missing)
            self.conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.cursor = self.conn.cursor()

            # Create tables if missing
            self.create_tables()
            self.guest_transactions = []

        except Exception as e:
            print("DB INIT ERROR:", e)
            self.conn = None
            self.cursor = None
            self.guest_transactions = []

    # --------------------------
    # CREATE TABLES
    # --------------------------

    def create_tables(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password BLOB NOT NULL
                )
            """
            )

            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """
            )

    # --------------------------
    # PASSWORD SECURITY
    # --------------------------

    def hash_password(self, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return salt + key

    def verify_password(self, stored_password, provided_password):
        salt = stored_password[:32]
        stored_key = stored_password[32:]
        new_key = hashlib.pbkdf2_hmac(
            "sha256", provided_password.encode("utf-8"), salt, 100000
        )
        return new_key == stored_key

    # --------------------------
    # USER METHODS
    # --------------------------

    def create_user(self, username, password):
        try:
            hashed_password = self.hash_password(password)
            with self.conn:
                self.conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def validate_user(self, username, password):
        cursor = self.conn.execute(
            "SELECT id, password FROM users WHERE username=?", (username,)
        )
        result = cursor.fetchone()

        if result:
            user_id, stored_password = result
            if self.verify_password(stored_password, password):
                return user_id
        return None

    # --------------------------
    # TRANSACTION METHODS
    # --------------------------

    def add_transaction(self, user_id, amount, category, date, t_type):
        if user_id is None:
            self.guest_transactions.append(
                {
                    "id": len(self.guest_transactions) + 1,
                    "amount": amount,
                    "category": category,
                    "date": date,
                    "type": t_type,
                }
            )
            return

        try:
            with self.conn:  # ✅ auto commit + prevents locking
                self.conn.execute(
                    """
                    INSERT INTO transactions (user_id, amount, category, date, type)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, amount, category, date, t_type),
                )

        except sqlite3.OperationalError as e:
            print("DB ERROR (ADD):", e)

    def get_all_transactions(self, user_id):
        if user_id is None:
            return [
                (t["id"], t["amount"], t["category"], t["date"], t["type"])
                for t in self.guest_transactions
            ]

        try:
            cursor = self.conn.execute(
                """
                SELECT id, amount, category, date, type
                FROM transactions
                WHERE user_id = ?
                ORDER BY date DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            print("DB ERROR (FETCH):", e)
        return []

    def delete_transaction(self, user_id, transaction_id):
        if user_id is None:
            self.guest_transactions = [
                t for t in self.guest_transactions if t["id"] != int(transaction_id)
            ]
            return

        try:
            with self.conn:
                self.conn.execute(
                    "DELETE FROM transactions WHERE id = ? AND user_id = ?",
                    (transaction_id, user_id),
                )
        except sqlite3.OperationalError as e:
            print("DB ERROR (DELETE):", e)

    def update_transaction(self, user_id, transaction_id, amount, category, date):
        if user_id is None:
            for t in self.guest_transactions:
                if t["id"] == int(transaction_id):
                    t["amount"] = amount
                    t["category"] = category
                    t["date"] = date
                    return

        try:
            with self.conn:
                self.conn.execute(
                    """
                    UPDATE transactions
                    SET amount = ?, category = ?, date = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (amount, category, date, transaction_id, user_id),
                )
        except sqlite3.OperationalError as e:
            print("DB ERROR (UPDATE):", e)

    def transaction_belongs_to_user(self, user_id, transaction_id):
        if user_id is None:
            return any(t["id"] == int(transaction_id) for t in self.guest_transactions)

        cursor = self.conn.execute(
            "SELECT 1 FROM transactions WHERE id=? AND user_id=?",
            (transaction_id, user_id),
        )
        return cursor.fetchone() is not None

    def reset_user_transactions(self, user_id):
        if user_id is None:
            self.guest_transactions = []
            return

        with self.conn:
            self.conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))

    # --------------------------
    # UTILITIES
    # --------------------------

    def close(self):
        try:
            self.conn.commit()
        except Exception as e:
            print("DB CLOSE ERROR:", e)
        finally:
            self.conn.close()
