from typing import List
from app.db.repos.cart_repo import CartRepo
from app.db.repos.cart_item_repo import CartItemRepo
from app.models.cart import Cart
from app.models.cart_item import CartItem


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
