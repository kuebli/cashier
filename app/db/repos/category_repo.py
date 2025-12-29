import sqlite3
from typing import List
from app.db.db import DB
from app.models.category import Category
from datetime import datetime


class CategoryRepo:
    def __init__(self, db: DB) -> None:
        self.db = db

    def create(self, name: str) -> int | None:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO categories (name) VALUES(?)", (name,))
                return cur.lastrowid
        except sqlite3.Error as e:
            print("DB Error: ", e)
            return None

    def get_one(self, id: int) -> Category | None:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, name, created_at, updated_at FROM categories WHERE id = ?",
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Category(
                    id=row["id"],
                    name=row["name"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
        except Exception as e:
            print("DB Error: ", e)
            return None

    def get_all(self) -> List[Category]:
        try:
            with self.db.connect() as conn:
                categories = []
                cur = conn.cursor()
                cur.execute("SELECT id, name, created_at, updated_at FROM categories")
                rows = cur.fetchall()
                for row in rows:
                    categories.append(
                        Category(
                            id=row["id"],
                            name=row["name"],
                            created_at=datetime.fromisoformat(row["created_at"]),
                            updated_at=datetime.fromisoformat(row["updated_at"]),
                        )
                    )
                return categories
        except sqlite3.Error as e:
            print("DB Error: ", e)
            return []

    def update(self, category: Category) -> bool:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE categories SET name = ? WHERE id = ?",
                    (category.name, category.id),
                )
                return cur.rowcount == 1
        except sqlite3.Error as e:
            print("DB Error: ", e)
            return False

    def delete(self, category: Category) -> bool:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute("DELETE from categories WHERE id = ?", (category.id,))
                return cur.rowcount == 1
        except sqlite3.Error as e:
            print("DB Error: ", e)
            return False
