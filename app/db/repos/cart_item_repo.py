from datetime import datetime
import sqlite3
from typing import List, Optional
from app.db.db import DB
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.cart_repo import CartRepo
from app.models.cart import Cart
from app.models.article import Article
from app.models.cart_item import CartItem


class CartItemRepo:
    def __init__(self, db: DB, cart_repo: CartRepo, article_repo: ArticleRepo) -> None:
        self.db = db
        self.cart_repo = cart_repo
        self.article_repo = article_repo

    def create(self, cart: Cart, article: Article, quantity: int) -> int | None:
        try:
            if (
                self.cart_repo.get_one(cart.id) is None
                or self.article_repo.get_one(article.id) is None
            ):
                print(
                    f"Cart with id {cart.id} or article with id {article.id} does not extist"
                )
                return None
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO m2m_carts_articles (article_id, cart_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                    (article.id, cart.id, quantity, article.price),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            print(
                f"CartItem for cart id {cart.id} and article id {article.id}, already exists"
            )
            return None
        except Exception as e:
            print("DB Error: ", e)
            return None

    def get_one(self, cart_item_id: int) -> Optional[CartItem]:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, article_id, cart_id, quantity, unit_price, created_at, updated_at FROM m2m_carts_articles WHERE id =?",
                    (cart_item_id,),
                )
                row = cur.fetchone()

                if row is None:
                    return None

                return CartItem(
                    id=row["id"],
                    article_id=row["article_id"],
                    cart_id=row["cart_id"],
                    quantity=row["quantity"],
                    unit_price=row["unit_price"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )

        except Exception as e:
            print("DB Error: ", e)
            return None

    def get_all(self, cart: Optional[Cart] = None) -> List[CartItem]:
        try:
            if cart is not None and self.cart_repo.get_one(cart.id) is None:
                print(f"Cart with id {cart.id} does not exist")
                return []
            with self.db.connect() as conn:
                cur = conn.cursor()
                if cart is not None:
                    cur.execute(
                        "SELECT id, article_id, cart_id, quantity, unit_price, created_at, updated_at from m2m_carts_articles WHERE cart_id = ?",
                        (cart.id,),
                    )
                else:
                    cur.execute(
                        "SELECT id, article_id, cart_id, quantity, unit_price, created_at, updated_at from m2m_carts_articles"
                    )
                rows = cur.fetchall()
                cart_items = []
                for row in rows:
                    cart_items.append(
                        CartItem(
                            id=row["id"],
                            article_id=row["article_id"],
                            cart_id=row["cart_id"],
                            quantity=row["quantity"],
                            unit_price=row["unit_price"],
                            created_at=datetime.fromisoformat(row["created_at"]),
                            updated_at=datetime.fromisoformat(row["updated_at"]),
                        )
                    )
                return cart_items
        except Exception as e:
            print("DB Error: ", e)
            return []

    def update(self, cart_item: CartItem) -> bool:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE m2m_carts_articles SET quantity = ?, unit_price = ? WHERE id = ?",
                    (cart_item.quantity, cart_item.unit_price, cart_item.id),
                )
                return cur.rowcount == 1
        except Exception as e:
            print("DB Error: ", e)
            return False

    def delete(self, cart_item: CartItem) -> bool:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "DELETE from m2m_carts_articles WHERE id = ?", (cart_item.id,)
                )
                return cur.rowcount == 1
        except Exception as e:
            print("DB Error: ", e)
            return False
