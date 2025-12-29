import sqlite3


class DB:
    def __init__(self, db_name: str = "cashier.db") -> None:
        self.__db_name = db_name

        self.conn = sqlite3.connect(self.__db_name)

        # enforce foreign keys for this connection
        self.conn.execute("PRAGMA foreign_keys = ON")

        self.__init_schema()

    def __init_schema(self) -> None:
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price FLOAT NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
        """)

    def connect(self) -> sqlite3.Connection:
        return self.conn

    def close(self) -> None:
        self.conn.close()

