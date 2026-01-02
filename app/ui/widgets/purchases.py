from typing import Optional
from textual.containers import Horizontal, HorizontalGroup, Vertical
from textual.widget import Widget
from textual.widgets import DataTable, Label, Markdown, Switch
from app.services.cart_service import CartService
from app.factories.receipt_builder import ReceiptBuilder


class Purchases(Widget):
    def __init__(self, cart_service: CartService):
        super().__init__()
        self.__cart_service = cart_service
        self.__receipt_builder = ReceiptBuilder()
        self.__cart_item_selected: Optional[int] = None
        self.__show_paid_only: bool = False

    def compose(self):
        yield (
            Horizontal(
                Vertical(
                    Label("Carts"),
                    DataTable(id="purchases_carts_table"),
                    HorizontalGroup(
                        Label(
                            "Show paid carts only", id="purchases_carts_switch_label"
                        ),
                        Switch(False, id="purchases_carts_switch"),
                        classes="push_right",
                    ),
                    id="purchases_carts",
                ),
                Vertical(
                    Label("Receipt"),
                    Markdown(
                        "Select a completed cart to view receipt",
                        id="purchases_receipt_markdown",
                    ),
                    id="purchases_receipt",
                ),
                id="purchases_content",
            )
        )

    def on_mount(self) -> None:
        table = self.query_one("#purchases_carts_table", DataTable)
        table.add_columns("ID", "Status", "Paid at", "Created at")
        self.__refresh_carts()

    def __refresh_carts(self) -> None:
        table = self.query_one("#purchases_carts_table", DataTable)
        table.clear(columns=False)
        self.__cart_item_selected = None
        carts = self.__cart_service.get_carts()
        if self.__show_paid_only:
            carts_filtered = [cart for cart in carts if cart.paid]
        else:
            carts_filtered = carts
        for cart in carts_filtered:
            status = "Completed" if cart.paid else "Open"
            table.add_row(
                str(cart.id),
                status,
                cart.paid_at.strftime("%d.%m.%Y %H:%M") if cart.paid_at else "",
                cart.created_at.strftime("%d.%m.%Y %H:%M") if cart.created_at else "",
            )

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if event.data_table.id != "purchases_carts_table":
            return
        self.query_one("#purchases_receipt_markdown", Markdown).update(
            "Select a completed cart to view receipt"
        )
        table = event.data_table
        row_key = event.cell_key.row_key
        row = table.get_row(row_key)
        self.__cart_item_selected = int(row[0])
        receipt_model = self.__cart_service.get_receipt(self.__cart_item_selected)
        if receipt_model:
            if receipt_model.paid_at is not None:
                reciept = self.__receipt_builder.build(receipt_model)
                self.query_one("#purchases_receipt_markdown", Markdown).update(reciept)

    def on_switch_changed(self, event: Switch.Changed):
        if event.switch.id == "purchases_carts_switch":
            sw = self.query_one("#purchases_carts_switch", Switch)
            self.__show_paid_only = sw.value
            self.__refresh_carts()
            self.__cart_item_selected = None
            self.query_one("#purchases_receipt_markdown", Markdown).update(
                "Select a completed cart to view receipt"
            )
