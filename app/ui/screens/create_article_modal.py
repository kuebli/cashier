from typing import List
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

from app.models.category import Category


class CreateArticleModal(ModalScreen[dict | None]):
    def __init__(self, categories: List[Category]) -> None:
        super().__init__()
        self.__categories = [(c.name, str(c.id)) for c in categories]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Create Article"),
            Input(placeholder="Name", id="create_article_name"),
            Input(
                placeholder="Price, e.g. 2.5", id="create_article_price", type="number"
            ),
            Select(id="create_article_categories", options=self.__categories),
            HorizontalGroup(
                Button(
                    label="Create Article",
                    variant="success",
                    id="create_article_button_create",
                    flat=True,
                ),
                Button(
                    label="Cancel",
                    variant="default",
                    id="create_article_button_cancel",
                    flat=True,
                ),
            ),
            classes="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_article_button_cancel":
            self.dismiss(None)
            return

        if event.button.id == "create_article_button_create":
            name = self.query_one("#create_article_name", Input).value.strip()
            price_raw = self.query_one("#create_article_price", Input).value.strip()
            category_raw = self.query_one("#create_article_categories", Select).value

            if not name or price_raw is None or category_raw is None:
                self.app.notify(
                    "All Name, Price and Category are required", severity="warning"
                )
                return

            try:
                price = float(price_raw)
                category = int(category_raw)
            except ValueError:
                return

            if price <= 0:
                self.app.notify("Price must be a positive number", severity="warning")
                return

            self.dismiss(
                {
                    "name": name,
                    "price": float(price),
                    "category_id": int(category),
                }
            )
