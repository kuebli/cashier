from textual.app import App
from textual.widgets import Header, Footer, TabPane, TabbedContent

from app.db.db import DB
from app.db.repos.category_repo import CategoryRepo
from app.db.repos.article_repo import ArticleRepo
from app.db.repos.cart_repo import CartRepo
from app.db.repos.cart_item_repo import CartItemRepo

from app.services.checkout_service import CheckoutService
from app.services.inventory_service import InventoryService
from app.services.cart_service import CartService
from app.ui.widgets.purchases import Purchases
from app.ui.widgets.checkout import Checkout
from app.ui.widgets.inventory import Inventory


class CashierApp(App):
    CSS_PATH = ["./styles/main.tcss"]
    TITLE = "Cashier"

    def __init__(self):
        super().__init__()
        self.__db = DB("cashier.db")

        # repos
        category_repo = CategoryRepo(self.__db)
        article_repo = ArticleRepo(self.__db, category_repo)
        cart_repo = CartRepo(self.__db)
        cart_item_repo = CartItemRepo(self.__db, cart_repo, article_repo)

        # services
        self.__checkout_service = CheckoutService(
            article_repo, cart_repo, cart_item_repo
        )
        self.__inventory_service = InventoryService(category_repo, article_repo)
        self.__cart_service = CartService(cart_repo, cart_item_repo)

    def on_exit(self) -> None:
        self.__db.close()

    def compose(self):
        yield Header()
        with TabbedContent(id="nav", initial="checkout"):
            with TabPane(title="Checkout", id="checkout"):
                yield Checkout(self.__checkout_service)
            with TabPane(title="Inventory", id="inventory"):
                yield Inventory(self.__inventory_service)
            with TabPane(title="Purchases", id="purchases"):
                yield Purchases(self.__cart_service)
        yield Footer()
