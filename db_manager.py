import sqlite3

class DatabaseManager:
    def __init__(self, db_name="finance.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()  # Creates transactions table
        self.create_user_table()  # Ensures user table exists

    # ----- USER METHODS -----
    def create_user_table(self):
        """Create the users table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        self.conn.commit()

    def create_user(self, username, password):
        """Create a new user account."""
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # username already exists

    def validate_user(self, username, password):
        """Check if login credentials are correct."""
        self.cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )
        result = self.cursor.fetchone()
        return result is not None

    # ----- TRANSACTIONS METHODS -----
    def create_tables(self):
        """Create the transactions table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                date TEXT,
                type TEXT
            )
        """)
        self.conn.commit()

    def add_transaction(self, amount, category, date, t_type):
        self.cursor.execute(
            "INSERT INTO transactions (amount, category, date, type) VALUES (?, ?, ?, ?)",
            (amount, category, date, t_type)
        )
        self.conn.commit()

    def delete_transaction(self, tid):
        self.cursor.execute("DELETE FROM transactions WHERE id=?", (tid,))
        self.conn.commit()

    def update_transaction(self, tid, amount, category, date):
        self.cursor.execute(
            """
            UPDATE transactions
            SET amount = ?, category = ?, date = ?
            WHERE id = ?
            """,
            (amount, category, date, tid)
        )
        self.conn.commit()

    def get_all_transactions(self):
        self.cursor.execute(
            "SELECT id, amount, category, date, type FROM transactions"
        )
        return self.cursor.fetchall()

    def get_transactions_filtered(self, category=None, start_date=None, end_date=None):
        query = "SELECT id, amount, category, date, type FROM transactions WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def reset_database(self):
        """Delete all transactions."""
        self.cursor.execute("DELETE FROM transactions")
        self.conn.commit()
