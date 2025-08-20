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

from textual.reactive import reactive
from textual.widget import Widget


class Pattern(Widget):
    pattern = reactive("")

    def render(self) -> str:
        return self.pattern

    def __str__(self):
        return self.pattern

    def empty(self):
        """Checks if pattern is empty"""
        return Pattern.pattern == ""


class Sample(Widget):
    sample = reactive("")

    def render(self) -> str:
        return self.sample

    def __str__(self):
        return self.sample

    def empty(self):
        """Checks if sample is empty."""
        return Sample.sample == ""


class Outcome(Widget):
    outcome: reactive[dict[str, str]] = reactive(list[dict], recompose=True, init=False)

    def render(self) -> str:
        return self.outcome

    def __str__(self):
        return self.outcome
