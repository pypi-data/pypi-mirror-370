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

import re

from textual import log

from dismew.errors import (
    DuplicateSemanticError,
    SemanticNotValidIdentifierError,
    UnknownPatternError,
)
from dismew.pattern_file_handler import PatternFileHandler

GROK_PATTERN_FORMAT = re.compile(r"%{([A-Z0-9_]+):(\w+)(?::\w+)?}")
PATTERN_REFERENCE = re.compile(r"%{(\w+)}")


class GrokPatternHandler:
    # Used to know what to show in the outcome
    # section of the program
    duplicate_semantic_detected = False
    unknown_pattern_key_detected = False
    invalid_semantic_identifier_detected = False

    def __init__(self):
        self.loaded_patterns = PatternFileHandler.get_loaded_patterns()
        self.pattern_replacement = ""
        self.results: list[dict] = []

    def compile(self, pattern_value: str) -> str:
        """
        Performs replacement, e.g. `%{USER:user} ESIM`
        will be `(?P<user>[a-zA-Z0-9._-]+) ESIM`
        """
        semantics_in_use = set()
        pattern_replacement = re.sub(
            GROK_PATTERN_FORMAT,
            lambda m: self.__check_pattern_and_semantic_validity(m, semantics_in_use),
            pattern_value,
        )
        log.debug(f"semantics being used = {semantics_in_use}")
        log.debug(f"pattern replacement = {pattern_replacement}")
        self.pattern_replacement = pattern_replacement
        return pattern_replacement

    def dictify_pattern_matches(self, sample_text: str):
        """Makes matches into a dictionary - will be used for display purposes."""
        results: list[dict] = []
        try:
            for line in sample_text:
                one = re.search(self.pattern_replacement, line.__str__()).groupdict()
                results.append(one)
            self.results = results
        except AttributeError:
            pass

    def __check_for_duplicate_semantic(self, semantic: str, semantics_in_use: set) -> None:
        if semantic in semantics_in_use:
            self.duplicate_semantic_detected = True
            raise DuplicateSemanticError(duplicate=semantic)
        semantics_in_use.add(semantic)

    def __check_pattern_and_semantic_validity(self, m, semantics_in_use) -> str:
        try:
            pattern = self.loaded_patterns[m.group(1)]
            semantic = str(m.group(2))

            if not semantic.isidentifier():
                self.invalid_semantic_identifier_detected = True
                raise SemanticNotValidIdentifierError(semantic[0])

            self.__check_for_duplicate_semantic(semantic=semantic, semantics_in_use=semantics_in_use)

            pattern = self.__replace_pattern_reference_with_regex(this_pattern=pattern)
        except KeyError:
            self.unknown_pattern_key_detected = True
            raise UnknownPatternError(known_patterns=PatternFileHandler.get_loaded_patterns().keys()) from KeyError
        except re.error:
            pass
        else:
            return f"(?P<{semantic}>{pattern})"

    def __replace_pattern_reference_with_regex(self, this_pattern) -> str:
        """
        Recursively replace grok pattern references with the regex the
        reference is refering to.
        """
        while True:
            new_pattern = re.sub(
                PATTERN_REFERENCE,
                lambda m: "(" + self.loaded_patterns[m.group(1)] + ")",
                this_pattern,
            )
            if new_pattern == this_pattern:
                break
            this_pattern = new_pattern
        return this_pattern
