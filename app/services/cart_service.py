from typing import List, Optional
from app.db.repos.cart_repo import CartRepo
from app.db.repos.cart_item_repo import CartItemRepo
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem


class CartService:
    def __init__(self, cart_repo: CartRepo, cart_item_repo: CartItemRepo) -> None:
        self.cart_repo = cart_repo
        self.cart_item_repo = cart_item_repo

    def get_carts(self) -> List[Cart]:
        return self.cart_repo.get_all()

    def get_cart_items(self, cart_id: int) -> List[CartItem]:
        cart = self.cart_repo.get_one(cart_id)
        if cart is None:
            return []
        return self.cart_item_repo.get_all(cart=cart)

    def get_receipt(self, cart_id: int) -> Optional[Receipt]:
        cart = self.cart_repo.get_one(cart_id)
        if cart and cart.paid_at is not None:
            cart_items = self.get_cart_items(cart.id)
            receipt_items: List[ReceiptItem] = []
            for cart_item in cart_items:
                receipt_items.append(
                    ReceiptItem(
                        cart_item.article_name, cart_item.quantity, cart_item.unit_price
                    )
                )
            return Receipt(
                cart.paid_at,
                receipt_items,
            )
        return
