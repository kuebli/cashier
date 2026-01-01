from datetime import date, datetime
from typing import List, Optional
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.cart_item_repo import CartItemRepo
from app.db.repos.cart_repo import CartRepo
from app.models.article import Article
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem


class CheckoutService:
    def __init__(
        self,
        article_repo: ArticleRepo,
        cart_repo: CartRepo,
        cart_item_repo: CartItemRepo,
    ) -> None:
        self.article_repo = article_repo
        self.cart_repo = cart_repo
        self.cart_item_repo = cart_item_repo
        self.__cart: Optional[Cart] = None
        self.__cart_items: List[CartItem] = []

    def __create_cart(self) -> Cart:
        """
        inserts a new cart into the database and returns the model instance
        """
        cart_id = self.cart_repo.create()
        if cart_id is None:
            raise Exception("Cart could not be created")

        cart = self.cart_repo.get_one(cart_id)
        if cart is None:
            raise RuntimeError(f"Cart with id {cart_id} could not be found")

        return cart

    def reset(self) -> None:
        """
        clears __cart and __cart_items and sets them to the initial state
        used when user aborts checkout or the checkout is done
        """
        self.__cart_items = []
        self.__cart = self.__create_cart()

    def search_article(self, search_text: str) -> List[Article]:
        """
        returns a list of articles found with the search_text
        search will be done case insensitive
        """
        return self.article_repo.get_all(search_text=search_text)

    def add_article(self, article: Article, quantity: int) -> bool:
        """
        creates a new cart_item on the database and appends it to __carts_items
        if a cart_item already exists, the quantity will be incremented accordingly
        """
        if self.__cart is None:
            self.__cart = self.__create_cart()

        for item in self.__cart_items:
            if item.article_id == article.id:
                item.quantity += quantity
                updated = self.cart_item_repo.update(item)
                if updated:
                    return True
                item.quantity -= quantity
                return False

        cart_item_id = self.cart_item_repo.create(self.__cart, article, quantity)
        if cart_item_id is None:
            return False

        new_cart_item = self.cart_item_repo.get_one(cart_item_id)
        if new_cart_item is not None:
            self.__cart_items.append(new_cart_item)
            return True

        return False

    def remove_article(self, cart_item_id: int) -> bool:
        """
        deletes cart_item on the database and removes it from __carts_items
        """
        cart_item = self.cart_item_repo.get_one(cart_item_id)
        if cart_item is None:
            return False

        deleted = self.cart_item_repo.delete(cart_item)
        if deleted:
            self.__cart_items.remove(cart_item)
            return True

        return False

    def get_cart_items(self) -> List[CartItem]:
        if self.__cart is None:
            return []
        return self.cart_item_repo.get_all(self.__cart)

    def checkout(self) -> Optional[Receipt]:
        """
        updates the cart entity in the database and sets paid = true and paid_at to current timestamp
        returns a Receipt Model
        """
        if self.__cart is not None and len(self.__cart_items) > 0:
            self.__cart.paid = True
            self.__cart.paid_at = datetime.now()
            if self.cart_repo.update(self.__cart):
                receipt_items = []
                for item in self.__cart_items:
                    receipt_items.append(
                        ReceiptItem(
                            article_name=item.article_name,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                        )
                    )
                reciept = Receipt(self.__cart.paid_at, receipt_items)
                self.__cart = None
                return reciept

        return None
