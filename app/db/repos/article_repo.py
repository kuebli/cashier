from typing import List, Optional
from app.db.db import DB
from app.db.repos.category_repo import CategoryRepo
from app.models.article import Article
from datetime import datetime


class ArticleRepo:
    def __init__(self, db: DB, category_repo: CategoryRepo) -> None:
        self.db = db
        self.category_repo = category_repo

    def create(self, name: str, price: float, category_id: int) -> int | None:
        try:
            if not self.category_repo.get_one(category_id):
                raise ValueError(f"Category with id {category_id} not found")
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO articles (name, price, category_id) VALUES(?,?,?)",
                    (name, price, category_id),
                )
                return cur.lastrowid
        except Exception as e:
            print("Database Error: ", e)
            return None

    def get_one(self, id: int) -> Article | None:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, name, price, category_id, created_at, updated_at FROM articles WHERE id = ?",
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None

                return Article(
                    id=row["id"],
                    name=row["name"],
                    price=row["price"],
                    category_id=row["category_id"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
        except Exception as e:
            print("Database Error: ", e)
            return None

    def get_all(
        self, category_id=None, search_text: Optional[str] = None
    ) -> List[Article]:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                query = "SELECT id, name, price, category_id, created_at, updated_at FROM articles"
                params = []

                if category_id is not None:
                    if self.category_repo.get_one(category_id) is None:
                        raise ValueError(f"Category with id {category_id} not found")
                    else:
                        query += " WHERE category_id = ?"
                        params.append(category_id)

                if search_text is not None:
                    query += " AND" if "WHERE" in query else " WHERE"
                    query += " name LIKE ?"
                    params.append(f"%{search_text}%")

                cur.execute(query, params)
                rows = cur.fetchall()
                articles = []
                for row in rows:
                    articles.append(
                        Article(
                            id=row["id"],
                            name=row["name"],
                            price=row["price"],
                            category_id=row["category_id"],
                            created_at=datetime.fromisoformat(row["created_at"]),
                            updated_at=datetime.fromisoformat(row["updated_at"]),
                        )
                    )
                return articles
        except Exception as e:
            print("Database Error: ", e)
            return []

    def update(self, article: Article) -> bool:
        try:
            if self.category_repo.get_one(article.category_id) is None:
                raise ValueError(f"Category with ID {article.category_id} not found")
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE articles SET name = ?, price = ?, category_id = ? WHERE id = ?",
                    (article.name, article.price, article.category_id, article.id),
                )
                return cur.rowcount == 1
        except Exception as e:
            print("DB Error: ", e)
            return False

    def delete(self, article: Article) -> bool:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM articles WHERE id = ?", (article.id,))
                return cur.rowcount == 1
        except Exception as e:
            print("DB Error: ", e)
            return False
