from textual.containers import HorizontalGroup, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class CreateCategoryModal(ModalScreen):
    def compose(self):
        yield Vertical(
            Label("Create Category"),
            Input(id="create_category_name"),
            HorizontalGroup(
                Button(
                    label="Create",
                    variant="success",
                    id="create_category_submit",
                    flat=True,
                ),
                Button(
                    label="Cancel",
                    variant="default",
                    id="create_category_cancel",
                    flat=True,
                ),
            ),
            classes="dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#create_category_name").focus()
        self.log("modal CreateCategoryModal opened")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        print("pressed")
        if event.button.id == "create_category_submit":
            name = self.query_one("#create_category_name", Input).value.strip()
            if not name:
                return
            self.dismiss(name)

        if event.button.id == "create_category_cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.input.value.strip()
        if not name:
            return
        self.dismiss(name)
