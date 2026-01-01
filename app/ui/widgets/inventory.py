from typing import Optional
from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
)
from textual.widget import Widget
from textual.widgets import Button, DataTable, Label, ListItem, ListView

from app.services.inventory_service import InventoryService
from app.ui.screens.create_article_modal import CreateArticleModal
from app.ui.screens.create_category_modal import CreateCategoryModal


class Inventory(Widget):
    def __init__(self, inventory_service: InventoryService):
        super().__init__()
        self.__inventory_service = inventory_service

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                ListView(id="inventory_categories_list"),
                Button(
                    label="Create Category",
                    variant="primary",
                    flat=True,
                    id="inventory_categories_button_create",
                ),
                id="inventory_categories",
            ),
            Vertical(
                DataTable(id="inventory_articles_table"),
                Button(
                    label="Create Article",
                    variant="primary",
                    flat=True,
                    id="inventory_articles_button_create",
                ),
                id="inventory_articles",
            ),
            id="inventory_content",
        )

    def on_mount(self) -> None:
        table = self.query_one("#inventory_articles_table", DataTable)
        table.add_columns("ID", "Name", "Price", "Category", "Created at")

        self.refresh_categories()
        self.refresh_articles()

        self.query_one("#inventory_categories_list", ListView).focus()

    def refresh_categories(self) -> None:
        categories = self.__inventory_service.get_categories()
        lv = self.query_one("#inventory_categories_list", ListView)

        lv.clear()

        def repopulate():
            for category in categories:
                lv.append(ListItem(Label(category.name), id=f"cat-{category.id}"))

        self.call_after_refresh(repopulate)

    def refresh_articles(self, category_id: Optional[int] = None) -> None:
        articles = self.__inventory_service.get_articles(category_id)
        table = self.query_one("#inventory_articles_table", DataTable)
        table.clear(columns=False)

        for article in articles:
            created_at = (
                article.created_at.strftime("%d.%m.%y %H:%M")
                if article.created_at is not None
                else ""
            )
            table.add_row(
                str(article.id),
                article.name,
                f"{article.price}.2f",
                str(article.category_id),
                created_at,
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "inventory_categories_list":
            return
        item_id = event.item.id  # e.g. "cat-3"
        if item_id and item_id.startswith("cat-"):
            category_id = int(item_id.split("-", 1)[1])
            self.refresh_articles(category_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "inventory_categories_button_create":
                self.run_worker(self.__create_category_workflow(), exclusive=True)
            case "inventory_articles_button_create":
                self.run_worker(self.__create_article_workflow(), exclusive=True)
            case _:
                return

    async def __create_category_workflow(self) -> None:
        name = await self.app.push_screen_wait(CreateCategoryModal())
        if name is None:
            return

        category_id = self.__inventory_service.create_category(name)
        if category_id is None:
            return

        self.refresh_categories()

    async def __create_article_workflow(self) -> None:
        categories = self.__inventory_service.get_categories()
        if not categories:
            self.app.notify("Please create a category first.", severity="warning")
            return

        payload = await self.app.push_screen_wait(CreateArticleModal(categories))
        if payload is None:
            return

        article_id = self.__inventory_service.create_article(
            payload["name"], payload["price"], payload["category_id"]
        )
        if article_id is None:
            return

        self.refresh_articles(payload["category_id"])
