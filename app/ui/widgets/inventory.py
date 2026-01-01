from typing import Optional
from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    HorizontalGroup,
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
        self.__selected_category_id: Optional[int] = None
        self.__selected_article_id: Optional[int] = None

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                Label("Categories", classes="title"),
                ListView(id="inventory_categories_list"),
                HorizontalGroup(
                    Button(
                        label="Create Category",
                        variant="primary",
                        flat=True,
                        id="inventory_categories_button_create",
                    ),
                    Button(
                        label="Delete Category",
                        variant="error",
                        flat=True,
                        id="inventory_categories_button_delete",
                        disabled=True,
                    ),
                    id="inventory_categories_buttons",
                ),
                id="inventory_categories",
            ),
            Vertical(
                Label("Articles", classes="title"),
                DataTable(id="inventory_articles_table"),
                HorizontalGroup(
                    Button(
                        label="Create Article",
                        variant="primary",
                        flat=True,
                        id="inventory_articles_button_create",
                    ),
                    Button(
                        label="Delete Article",
                        variant="error",
                        flat=True,
                        id="inventory_articles_button_delete",
                        disabled=True,
                    ),
                ),
                id="inventory_articles",
            ),
            id="inventory_content",
        )

    async def on_mount(self) -> None:
        table = self.query_one("#inventory_articles_table", DataTable)
        table.add_columns("ID", "Name", "Price", "Category", "Created at")

        await self.refresh_categories()
        self.refresh_articles()

        self.query_one("#inventory_categories_list", ListView).focus()
        lv = self.query_one("#inventory_categories_list", ListView)
        lv.index = 0

    async def refresh_categories(self) -> None:
        categories = self.__inventory_service.get_categories()
        self.query_one("#inventory_categories_button_delete", Button).disabled = True
        lv = self.query_one("#inventory_categories_list", ListView)

        await lv.clear()

        await lv.append(ListItem(Label("(All)"), id="cat-all"))

        for category in categories:
            await lv.append(ListItem(Label(category.name), id=f"cat-{category.id}"))

    def refresh_articles(self) -> None:
        self.__selected_article_id = None
        self.query_one("#inventory_articles_button_delete", Button).disabled = True
        articles = self.__inventory_service.get_articles(self.__selected_category_id)
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
                str(article.price),
                str(article.category_id),
                created_at,
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "inventory_categories_list":
            return

        item_id = event.item.id

        if item_id == "cat-all":
            self.__selected_category_id = None
            self.query_one(
                "#inventory_categories_button_delete", Button
            ).disabled = True
            self.refresh_articles()
            return

        if item_id and item_id.startswith("cat-"):
            category_id = int(item_id.split("-", 1)[1])
            self.__selected_category_id = category_id
            self.query_one(
                "#inventory_categories_button_delete", Button
            ).disabled = False
            self.refresh_articles()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "inventory_categories_button_create":
                self.run_worker(self.__create_category_workflow(), exclusive=True)
            case "inventory_articles_button_create":
                self.run_worker(self.__create_article_workflow(), exclusive=True)
            case "inventory_articles_button_delete":
                self.run_worker(self.__delete_article_workflow(), exclusive=True)
            case "inventory_categories_button_delete":
                self.run_worker(self.__delete_category_workflow(), exclusive=True)
            case _:
                return

    async def __create_category_workflow(self) -> None:
        name = await self.app.push_screen_wait(CreateCategoryModal())
        if name is None:
            return

        category_id = self.__inventory_service.create_category(name)
        if category_id is None:
            return

        await self.refresh_categories()

    async def __delete_category_workflow(self) -> None:
        if self.__selected_category_id is None:
            return

        if self.__inventory_service.delete_category(self.__selected_category_id):
            self.app.notify("Category has been deleted.", severity="information")
            self.__selected_category_id = None
            self.query_one(
                "#inventory_categories_button_delete", Button
            ).disabled = True
            self.query_one("#inventory_articles_button_delete", Button).disabled = True
            await self.refresh_categories()
            self.refresh_articles()
        else:
            self.app.notify("Category could not be deleted", severity="warning")

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

        self.refresh_articles()

    async def __delete_article_workflow(self) -> None:
        if self.__selected_article_id is None:
            return

        deleted = self.__inventory_service.delete_article(self.__selected_article_id)
        if not deleted:
            self.app.notify("Could not delete article", severity="warning")
            return

        self.__selected_article_id = None
        self.query_one("#inventory_articles_button_delete", Button).disabled = True

        self.refresh_articles()

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if event.data_table.id != "inventory_articles_table":
            return

        table = event.data_table
        row_key = event.cell_key.row_key
        row = table.get_row(row_key)

        self.__selected_article_id = int(row[0])
        self.query_one("#inventory_articles_button_delete", Button).disabled = False
