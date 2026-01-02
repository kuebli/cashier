from datetime import datetime
from typing import List, Optional
from app.db.db import DB
from app.models.cart import Cart


class CartRepo:
    def __init__(self, db: DB) -> None:
        self.db = db

    def create(self) -> Optional[int]:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO carts DEFAULT VALUES")
                return cur.lastrowid

        except Exception as e:
            print("DB Error: ", e)
            return None

    def get_one(self, cart_id: int) -> Optional[Cart]:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, paid, paid_at, created_at, updated_at FROM carts WHERE id = ?",
                    (cart_id,),
                )
                row = cur.fetchone()

                if row is None:
                    return None

                items = []

                paid_at = (
                    datetime.fromisoformat(row["paid_at"])
                    if row["paid_at"] is not None
                    else None
                )

                return Cart(
                    id=row["id"],
                    paid=row["paid"],
                    paid_at=paid_at,
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    items=items,
                )

        except Exception as e:
            print("DB Error: ", e)
            return None

    def get_all(self) -> List[Cart]:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, paid, paid_at, created_at, updated_at FROM carts"
                )

                rows = cur.fetchall()
                carts = []

                for row in rows:
                    paid_at = (
                        datetime.fromisoformat(row["paid_at"])
                        if row["paid_at"] is not None
                        else None
                    )
                    carts.append(
                        Cart(
                            id=row["id"],
                            paid=row["paid"],
                            paid_at=paid_at,
                            created_at=datetime.fromisoformat(row["created_at"]),
                            updated_at=datetime.fromisoformat(row["updated_at"]),
                            items=[],
                        )
                    )

                return carts

        except Exception as e:
            print("DB Error: ", e)
            return []

    def update(self, cart: Cart) -> bool:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE carts SET paid = ?, paid_at = ? WHERE id = ?",
                    (cart.paid, cart.paid_at, cart.id),
                )

                return cur.rowcount == 1

        except Exception as e:
            print("DB Error: ", e)
            return False

    def delete(self, cart: Cart) -> bool:
        try:
            with self.db.connect() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM carts WHERE id = ?", (cart.id,))
                return cur.rowcount == 1

        except Exception as e:
            print("DB Error: ", e)
            return False
