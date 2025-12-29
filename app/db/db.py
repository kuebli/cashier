import sqlite3


class DB:
    def __init__(self, db_name: str = "cashier.db") -> None:
        self.__db_name = db_name
        self.__init_schema()

    def __connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.__db_name)

    def __init_schema(self) -> None:
        with self.__connect() as conn:
            cur = conn.cursor()

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

