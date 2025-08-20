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

import pytest

from typing import ClassVar

from dismew.errors import DefaultFileLoadError, PatternFileNotFoundError
from dismew.pattern_file_handler import PatternFileHandler


class TestPatternFileHandling:
    pfh: ClassVar[object] = PatternFileHandler()
    preloaded: ClassVar[str] = "grok-patterns"
    final_test_load: ClassVar[set[str]] = {}

    @classmethod
    def test_handle_load_empty(cls):
        with pytest.raises(DefaultFileLoadError):
            cls.pfh.handle_load(selected_pattern_files=[])

    @classmethod
    def test_handle_load_unknown(cls):
        file: str = "nosuchthing"
        with pytest.raises(PatternFileNotFoundError):
            cls.pfh.handle_load(selected_pattern_files=[file])

    @classmethod
    def test_handle_load_default(cls):
        """Test default load functionality"""
        given: list[str] = ["grok-patterns"]
        cls.pfh.handle_load(selected_pattern_files=given)
        expected: set[str] = {"grok-patterns"}
        assert cls.pfh.get_loaded_files() == expected

    @classmethod
    def test_handle_load_multiple(cls):
        given: list[str] = ["java", "exim", "mongodb"]
        cls.pfh.handle_load(selected_pattern_files=given)
        expected: set[str] = {cls.preloaded, "java", "exim", "mongodb"}
        assert cls.pfh.get_loaded_files() == expected

    @classmethod
    def test_handle_unload_single(cls):
        given: list[str] = ["java"]
        cls.pfh.handle_unload(deselected_pattern_files=given)
        expected: set[str] = {cls.preloaded, "exim", "mongodb"}
        assert cls.pfh.get_loaded_files() == expected

    @classmethod
    def test_handle_unload_multiple(cls):
        given: list[str] = ["exim", "mongodb"]
        cls.pfh.handle_unload(deselected_pattern_files=given)
        expected: set[str] = {cls.preloaded}
        assert cls.pfh.get_loaded_files() == expected

    @classmethod
    def test_handle_unload_default(cls):
        given: list[str] = [cls.preloaded]
        cls.pfh.handle_unload(deselected_pattern_files=given)
        expected: set[str] = {cls.preloaded}
        assert cls.pfh.get_loaded_files() == expected
