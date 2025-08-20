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

import codecs
import os
from functools import reduce
from typing import ClassVar

from dismew.errors import DefaultFileLoadError, PatternFileNotFoundError

CURRENT_DIRECTORY = os.path.dirname(__file__)
PATTERNS_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "./", "patterns")
FILE_TO_BE_PRELOADED = "grok-patterns"


class PatternFileHandler:
    loaded: ClassVar[dict[str, dict[str, str]]] = {}

    @classmethod
    def handle_load(cls, selected_pattern_files: list[str]) -> None:
        """Handles when to load patterns from a file."""
        if selected_pattern_files.__len__() > 1:
            for file in selected_pattern_files:
                if file not in cls.get_loaded_files():
                    cls.__load_patterns(filename=file)
        elif selected_pattern_files.__len__() == 1:
            default = selected_pattern_files[0]
            cls.__load_patterns(filename=default)
        else:
            raise DefaultFileLoadError

    @classmethod
    def handle_unload(cls, deselected_pattern_files: list[str]) -> None:
        """Unloads file and its contents from use."""
        for file in deselected_pattern_files:
            if file in cls.get_loaded_files() and file != FILE_TO_BE_PRELOADED:
                del cls.loaded[file]

    @classmethod
    def get_loaded_files(cls) -> set[str]:
        """Gets all the filenames that been loaded for use."""
        return cls.loaded.keys()

    @classmethod
    def get_loaded_patterns(cls) -> dict[str, str]:
        """Gets all of the patterns that have been loaded for use."""
        nested_dicts = list(cls.loaded.values())
        return reduce(lambda a, b: dict(a, **b), nested_dicts)

    @staticmethod
    def get_pattern_file_names() -> list[str]:
        """Gets all filenames in the 'patterns' directory."""
        return os.listdir(PATTERNS_DIRECTORY)

    @classmethod
    def __load_patterns(cls, filename: str):
        """Loads all patterns from a file for usage."""
        try:
            pattern_combo = {}  # pattern name : pattern regex
            with codecs.open(f"{PATTERNS_DIRECTORY}/{filename}", "r", encoding="utf-8") as pattern_file:
                for line in pattern_file:
                    stripped_line = line.strip()
                    if not stripped_line or stripped_line.startswith("#"):
                        continue
                    name, pattern = stripped_line.split(" ", maxsplit=1)
                    pattern_combo[name] = pattern
                cls.loaded[filename] = pattern_combo
        except FileNotFoundError:
            raise PatternFileNotFoundError(pattern_file=filename) from FileNotFoundError
