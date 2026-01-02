from typing import Optional
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import DataTable, Label, Markdown
from app.services.cart_service import CartService
from app.factories.receipt_builder import ReceiptBuilder


class Purchases(Widget):
    def __init__(self, cart_service: CartService):
        super().__init__()
        self.__cart_service = cart_service
        self.__receipt_builder = ReceiptBuilder()
        self.__cart_item_selected: Optional[int] = None

    def compose(self):
        yield (
            Horizontal(
                Vertical(
                    Label("Carts"),
                    DataTable(id="purchases_table"),
                ),
                Vertical(
                    Label("Receipt"),
                    Markdown(
                        id="purchases_receipt_markdown",
                    ),
                    id="purchases_receipt",
                ),
                id="purchases_content",
            )
        )

    def on_mount(self) -> None:
        carts = self.__cart_service.get_carts()
        table = self.query_one("#purchases_table", DataTable)
        table.add_columns("ID", "Status", "Paid at", "Created at")
        for cart in carts:
            status = "Completed" if cart.paid else "Open"
            table.add_row(
                str(cart.id),
                status,
                cart.paid_at.strftime("%d.%m.%Y %H:%M") if cart.paid_at else "",
                cart.created_at,
            )

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if event.data_table.id != "purchases_table":
            return
        self.query_one("#purchases_receipt_markdown", Markdown).update("")
        table = event.data_table
        row_key = event.cell_key.row_key
        row = table.get_row(row_key)
        self.__cart_item_selected = int(row[0])
        reciept_model = self.__cart_service.get_receipt(self.__cart_item_selected)
        if reciept_model:
            if reciept_model.paid_at is not None:
                reciept = self.__receipt_builder.build(reciept_model)
                self.query_one("#purchases_receipt_markdown", Markdown).update(reciept)
