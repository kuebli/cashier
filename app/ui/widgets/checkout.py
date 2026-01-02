from typing import List, Optional, Tuple
from textual.containers import Horizontal, HorizontalGroup, Vertical
from textual.widget import Widget
from textual.widgets import Button, DataTable, Digits, Input, Label, ListItem, ListView

from app.models.article import Article
from app.services.checkout_service import CheckoutService
from app.ui.screens.checkout_receipt_modal import CheckoutReceiptModal


class Checkout(Widget):
    def __init__(self, checkout_service: CheckoutService) -> None:
        super().__init__()
        self.__checkout_service = checkout_service
        self.__articles_found: List[Article] = []
        self.__article_selected: Optional[int] = None
        self.__cart_item_selected: Optional[int] = None
        self.quantity: List[Tuple[str, str]] = [(str(x), str(x)) for x in range(1, 10)]
        self.__search_timer = None

    def on_mount(self) -> None:
        self.query_one("#checkout_settings_article_search", Input).focus()
        table = self.query_one("#checkout_cart_items_table", DataTable)
        table.add_columns("ID", "Article", "Price", "Quantity", "Line Total")
        self.__refresh_cart_items()

    def compose(self):
        yield Horizontal(
            Vertical(
                Label("Cart"),
                DataTable(id="checkout_cart_items_table"),
                Button(
                    label="Remove Item",
                    variant="error",
                    id="checkout_cart_items_button_delete",
                    flat=True,
                    disabled=True,
                ),
                id="checkout_cart_items",
            ),
            Vertical(
                Label("Available Articles"),
                Input(
                    placeholder="Search Article...",
                    id="checkout_settings_article_search",
                ),
                ListView(id="checkout_settings_article_list"),
                HorizontalGroup(
                    Button(
                        "Add Article",
                        variant="primary",
                        id="checkout_settings_button_add",
                        flat=True,
                        disabled=True,
                    ),
                    classes="push_right",
                ),
                Vertical(
                    Label("Total"),
                    Digits(value="0", id="checkout_settings_total_display"),
                    HorizontalGroup(
                        Button(
                            "Abort",
                            variant="warning",
                            id="checkout_settings_button_abort",
                            flat=True,
                            disabled=True,
                        ),
                        Button(
                            "Checkout",
                            variant="success",
                            id="checkout_settings_button_checkout",
                            flat=True,
                            disabled=True,
                        ),
                        id="checkout_settings_buttons",
                    ),
                    id="checkout_settings_total",
                ),
                id="checkout_settings",
            ),
            id="checkout_content",
        )

    async def __refresh_articles(self) -> None:
        self.query_one("#checkout_settings_button_add", Button).disabled = True
        self.__article_selected = None
        lv = self.query_one("#checkout_settings_article_list", ListView)
        await lv.clear()
        if len(self.__articles_found) > 0:
            for article in self.__articles_found:
                await lv.append(
                    ListItem(
                        Label(f"{article.name} - CHF {article.price}"),
                        id=f"art-{article.id}",
                    )
                )

    def __refresh_cart_items(self) -> None:
        table = self.query_one("#checkout_cart_items_table", DataTable)
        table.clear(columns=False)
        cart_items = self.__checkout_service.get_cart_items()
        total = 0
        for cart_item in cart_items:
            line_total = cart_item.unit_price * cart_item.quantity
            total += line_total
            table.add_row(
                str(cart_item.id),
                cart_item.article_name,
                str(cart_item.unit_price),
                str(cart_item.quantity),
                f"CHF {line_total:.2f}",
            )
        self.query_one("#checkout_settings_total_display", Digits).update(
            f"{total:.2f}"
        )
        self.__cart_item_selected = None
        self.query_one("#checkout_cart_items_button_delete", Button).disabled = True

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "checkout_settings_article_search":
            return

        # Cancel previous debounce timer
        if self.__search_timer:
            self.__search_timer.stop()

        # Start a new debounce timer (300ms)
        text = event.input.value
        self.__search_timer = self.set_timer(
            0.3,
            lambda: self._perform_search(text),
        )

    def _perform_search(self, text: str) -> None:
        if len(text) < 2:
            self.__articles_found = []
            self.run_worker(self.__refresh_articles(), exclusive=True)
            return

        self.__articles_found = self.__checkout_service.search_article(text)
        self.run_worker(self.__refresh_articles(), exclusive=True)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "checkout_settings_article_list":
            id = event.item.id
            if id and id.startswith("art-"):
                self.__article_selected = int(id.split("-", 1)[1])
                self.query_one("#checkout_settings_button_add", Button).disabled = False

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if event.data_table.id != "checkout_cart_items_table":
            return
        table = event.data_table
        row_key = event.cell_key.row_key
        row = table.get_row(row_key)
        self.__cart_item_selected = int(row[0])
        self.query_one("#checkout_cart_items_button_delete", Button).disabled = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "checkout_settings_button_add":
                self.run_worker(self.__add_article_to_cart(), exclusive=True)
            case "checkout_cart_items_button_delete":
                self.run_worker(self.__remove_cart_item_from_cart(), exclusive=True)
            case "checkout_settings_button_abort":
                self.run_worker(self.__abort(), exclusive=True)
            case "checkout_settings_button_checkout":
                self.run_worker(self.__checkout(), exclusive=True)
            case _:
                return

    async def __add_article_to_cart(self) -> None:
        if self.__article_selected is not None:
            article = None
            for a in self.__articles_found:
                if a.id == self.__article_selected:
                    article = a
                    break
            if article is None:
                return
            added = self.__checkout_service.add_article(article, 1)
            if added:
                self.query_one(
                    "#checkout_settings_button_checkout", Button
                ).disabled = False
                self.query_one(
                    "#checkout_settings_button_abort", Button
                ).disabled = False
                self.__refresh_cart_items()

    async def __remove_cart_item_from_cart(self) -> None:
        if self.__cart_item_selected is not None:
            removed = self.__checkout_service.remove_article(self.__cart_item_selected)
            if removed:
                self.__cart_item_selected = None
                self.__refresh_cart_items()
                self.query_one(
                    "#checkout_cart_items_button_delete", Button
                ).disabled = True
                if len(self.__checkout_service.get_cart_items()) == 0:
                    self.query_one(
                        "#checkout_settings_button_checkout", Button
                    ).disabled = True
                    self.query_one(
                        "#checkout_settings_button_abort", Button
                    ).disabled = True

    async def __abort(self) -> None:
        self.__checkout_service.reset()
        await self.__reset()

    async def __checkout(self) -> None:
        receipt = self.__checkout_service.checkout()
        self.log("checkout", receipt)
        if receipt is not None:
            self.app.push_screen(CheckoutReceiptModal(receipt))
            await self.__reset()

    async def __reset(self) -> None:
        self.query_one("#checkout_cart_items_button_delete", Button).disabled = True
        self.query_one("#checkout_settings_button_add", Button).disabled = True
        self.query_one("#checkout_settings_button_checkout", Button).disabled = True
        self.query_one("#checkout_settings_button_abort", Button).disabled = True

        if self.__search_timer:
            self.__search_timer.stop()

        self.query_one("#checkout_settings_article_search", Input).value = ""
        self.__article_selected = None
        self.__cart_item_selected = None
        self.__articles_found = []

        self.__refresh_cart_items()
        await self.__refresh_articles()
