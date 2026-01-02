from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

from app.models.receipt import Receipt
from app.factories.receipt_builder import ReceiptBuilder


class CheckoutReceiptModal(ModalScreen):
    def __init__(self, receipt: Receipt):
        super().__init__()
        self.__reciept = receipt
        self.__reciept_builder = ReceiptBuilder()

    def compose(self):
        yield Vertical(
            Markdown(markdown=self.__reciept_builder.build(self.__reciept)),
            Button(
                label="Close",
                variant="error",
                id="checkout_receipt_modal_close",
                flat=True,
            ),
            classes="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "checkout_receipt_modal_close":
            self.dismiss()
