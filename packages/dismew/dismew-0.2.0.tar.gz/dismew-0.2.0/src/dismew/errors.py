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


class DefaultFileLoadError(ValueError):
    """Raised when no default has been given"""

    def __init__(self):
        self.msg = "This shouldn't happen, but if it does, bully the developer!"
        super().__init__(self.msg)


class DuplicateSemanticError(ValueError):
    """Raised when semantic already exists."""

    def __init__(self, duplicate: str):
        self.msg = (
            f"Duplicate semantic detected! "
            f"Update your Grok pattern input field so that you don't have duplicates. "
            f'Semantic that has a duplicate "{duplicate}"'
        )
        super().__init__(self.msg)


class UnknownPatternError(KeyError):
    """
    Raised when pattern key is not known to us, e.g. '%{THIS:my_semantic}',
    where 'THIS' is not listed in the patterns file.
    """

    def __init__(self, known_patterns: list[str]):
        self.msg = (f"Please only use these patterns: {known_patterns.__str__()}",)
        super().__init__(self.msg)


class SemanticNotValidIdentifierError(ValueError):
    """
    Raised when semantic in not a valid identifier,
    meaning it start with, for example, 2; therefore '%{USER:2}'
    is not valid.
    """

    def __init__(self):
        self.msg = (
            "You broke the semantic naming rule! "
            "Please make sure that the semantic, i.e. the right side "
            'of ":", is "within the ASCII range (U+0001..U+007F), '
            "the valid characters for identifiers include the uppercase and lowercase letters "
            'A through Z, the underscore _ and, except for the first character, the digits 0 through 9." '
            "- docs.python.org"
        )
        super().__init__(self.msg)


class PatternFileNotFoundError(FileNotFoundError):
    """
    Raised when program cannot find the pattern file.
    Note: this should not occur, since we use will have
    a predetermined list of pattern files which they can
    load.
    """

    def __init__(self, pattern_file: str):
        self.msg = f"Pattern file '{pattern_file}' not found."
        super().__init__(self.msg)
