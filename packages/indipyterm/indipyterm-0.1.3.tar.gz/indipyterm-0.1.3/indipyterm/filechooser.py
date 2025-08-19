from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.widgets import Button, DirectoryTree
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal



class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]


class FilePane(Container):

    DEFAULT_CSS = """

        FilePane {
            align: center middle;
            width: 70%;
            height: 70%;
            border: mediumvioletred;
            background: $panel;
           }

        FilteredDirectoryTree {
            margin: 1;
           }

        Horizontal {
            height: auto;
            align: right middle;
           }

        Button {
            margin-right: 2;
            }
        """

    def compose(self) -> ComposeResult:
        yield FilteredDirectoryTree("/")
        with Horizontal():
            yield Button("Cancel", variant="primary", id="cancel")
            yield Button("Send", variant="primary", id="send", disabled=True)

    def on_mount(self):
        self.border_title = "Choose File"





class ChooseFileSc(ModalScreen):
    """The class defining the choose file screen."""

    DEFAULT_CSS = """

        ChooseFileSc {
            align: center middle;
            }
        """

    def __init__(self):
        self.selected_filepath = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield FilePane()

    def on_directory_tree_directory_selected(self, event):
        "On a directory being selected, disable the send button"
        sndbtn = self.query_one("#send")
        sndbtn.disabled = True
        self.selected_filepath = None

    def on_directory_tree_file_selected(self, event):
        """On a file being selected, enable the send button
           and store the filepath"""
        sndbtn = self.query_one("#send")
        sndbtn.disabled = False
        self.selected_filepath = event.path

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        if event.button.id == "send":
            self.dismiss(self.selected_filepath)
