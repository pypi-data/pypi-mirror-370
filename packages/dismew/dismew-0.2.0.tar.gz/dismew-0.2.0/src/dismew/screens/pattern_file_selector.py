# Copyright (C) 2025 Spuzkov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from typing import ClassVar

from textual import log
from textual.app import ComposeResult, on
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.scroll_view import ScrollableContainer
from textual.widgets import Button, Checkbox

from dismew.pattern_file_handler import PatternFileHandler

READONLY_CHECKBOX_LABEL = "grok-patterns"
READONLY_CHECKBOX_ITEM = Checkbox(label=READONLY_CHECKBOX_LABEL, value=True, disabled=True)
SUBMIT_BUTTON = Button(label="Submit")


class PatternFileSelectorScreen(ModalScreen):
    """Shows list of selectable pattern files and description."""

    BINDINGS: ClassVar[list[(str, str, str)]] = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self):
        super().__init__()
        self.all_pattern_file_names = PatternFileHandler.get_pattern_file_names()
        self.loaded_files = PatternFileHandler.get_loaded_files()
        self.checkbox_items = self.__generate_checkbox_items()
        self.checked_items = []
        self.unchecked_items = []

    def compose(self) -> ComposeResult:
        with Vertical(classes="selector-modal-screen"):
            with ScrollableContainer(id="pattern-file-buttons"):
                yield from self.checkbox_items
                for _item in self.checkbox_items:
                    cb = _item
                    yield cb
            yield SUBMIT_BUTTON

    def on_mount(self):
        modal = self.query_one(Vertical)
        modal.border_title = "Load or Unload patterns for use."

    @on(Button.Pressed)
    def on_submit(self):
        if self.unchecked_items:
            PatternFileHandler.handle_unload(deselected_pattern_files=self.unchecked_items)
            log.info(f"Unloading patterns from: {self.loaded_files}")

        if self.checked_items:
            PatternFileHandler.handle_load(selected_pattern_files=self.checked_items)
            log.info(f"Loading patterns from: {self.loaded_files}")

        self.app.pop_screen()

    @on(Checkbox.Changed)
    def check_changed(self, event: Checkbox.Changed):
        label = event.checkbox.label
        log.info(f"{label} is {event.value}")
        match event.value:
            case True:
                if label in self.unchecked_items:
                    self.__remove_from_unchecked(filename=label)
                self.__add_to_checked(filename=label)
            case False:
                self.__remove_from_checked(filename=label)
                self.__add_to_unchecked(filename=label)
        log.info(f"Checked items: {self.checked_items}")
        log.info(f"Unchecked items: {self.unchecked_items}")

    def __add_to_checked(self, filename: str) -> None:
        self.checked_items.append(filename)
        log.info(f"{filename} has been added to checked.")

    def __add_to_unchecked(self, filename: str) -> None:
        self.unchecked_items.append(filename)
        log.info(f"{filename} has been added to unchecked.")

    def __remove_from_unchecked(self, filename: str) -> None:
        self.unchecked_items.remove(filename)
        log.info(f"{filename} has been removed from unchecked.")

    def __remove_from_checked(self, filename: str) -> None:
        self.checked_items.remove(filename)
        log.info(f"{filename} has been removed from checked.")

    def __generate_checkbox_items(self) -> list[Checkbox]:
        checkable_items: list[Checkbox(str)] = [READONLY_CHECKBOX_ITEM]
        for filename in self.all_pattern_file_names:
            if filename == READONLY_CHECKBOX_LABEL:
                continue
            checkable_items.append(Checkbox(filename))
        return checkable_items
