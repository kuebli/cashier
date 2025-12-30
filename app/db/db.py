import sqlite3


class DB:
    def __init__(self, db_name: str = "cashier.db") -> None:
        self.__db_name = db_name

        self.conn = sqlite3.connect(self.__db_name)

        # enforce foreign keys for this connection
        self.conn.execute("PRAGMA foreign_keys = ON")

        # get kw for fetchone and fetchall instead of index
        self.conn.row_factory = sqlite3.Row

        self.__init_schema()

    def __init_schema(self) -> None:
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price FLOAT NOT NULL,
            category_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paid BOOL NOT NULL DEFAULT FALSE,
            paid_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS m2m_carts_articles (
            id INTEGER PRIMARY KEY NOT NULL,
            article_id INTERGER NOT NULL,
            cart_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price float NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE CASCADE,
            FOREIGN KEY(cart_id) REFERENCES carts(id) ON DELETE CASCADE,
            UNIQUE(article_id, cart_id)
        )
        """)

        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS categories_updated_at
        AFTER UPDATE ON categories
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE categories
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
        """)

        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS articles_updated_at
        AFTER UPDATE ON articles
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE articles
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
        """)

        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS carts_updated_at
        AFTER UPDATE ON carts
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE carts
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
        """)

        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS m2m_carts_articles_updated_at
        AFTER UPDATE ON m2m_carts_articles
        FOR EACH ROW
        WHEN NEW.updated_at = OLD.updated_at
        BEGIN
            UPDATE m2m_carts_articles
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
        """)
        self.conn.commit()

    def connect(self) -> sqlite3.Connection:
        return self.conn

    def close(self) -> None:
        self.conn.close()
