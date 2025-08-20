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

from dismew.pattern_file_handler import PatternFileHandler
from dismew.pattern_handler import GrokPatternHandler


class TestPatternHandling:
    loaded = PatternFileHandler.handle_load(selected_pattern_files=["grok-patterns"])
    gph = GrokPatternHandler()

    def test_compile_pattern_that_has_no_references(self):
        """
        This tests a pattern that has no references to other patterns
        """
        given: str = "%{USERNAME:username}"
        expected: str = r"(?P<username>[a-zA-Z0-9._-]+)"
        assert self.gph.compile(pattern_value=given) == expected

    def test_compile_that_has_a_single_pattern_reference(self):
        """
        This tests a pattern that has a single reference
        to a pattern which doesn't have references.
        """
        # references USERNAME in grok-patterns file
        given: str = "%{USER:username}"
        expected: str = r"(?P<username>([a-zA-Z0-9._-]+))"
        assert self.gph.compile(pattern_value=given) == expected

    def test_compile_pattern_that_has_multiple_references(self):
        """
        This tests a pattern that has more than 1 references
        to other patterns that do not reference to other patterns.
        """
        given: str = "%{EMAILADDRESS:email}"
        expected: str = (
            r"(?P<email>([a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~]{1,64}"
            r"(?:\.[a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~]{1,62}){0,63})"
            r"@(\b(?:[0-9A-Za-z][0-9A-Za-z-]{0,62})(?:\.(?:"
            r"[0-9A-Za-z][0-9A-Za-z-]{0,62}))*(\.?|\b)))"
        )
        assert self.gph.compile(pattern_value=given) == expected

    def test_compile_pattern_that_has_reference_recursion(self):
        """
        This tests a pattern that has 'pattern reference recursion',
        meaning reference to pattern has a reference to a pattern,
        and so on.
        """
        given: str = "%{DATESTAMP_RFC2822:references}"
        expected: str = (
            r"(?P<references>((?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)"
            r"?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)), "
            r"((?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])) (\b(?:"
            r"[Jj]an(?:uary|uar)?|[Ff]eb(?:ruary|ruar)?|[Mm](?:a|ä)"
            r"?r(?:ch|z)?|[Aa]pr(?:il)?|[Mm]a(?:y|i)?|[Jj]un(?:e|i)?|"
            r"[Jj]ul(?:y|i)?|[Aa]ug(?:ust)?|[Ss]ep(?:tember)?|[Oo](?:c|k)"
            r"?t(?:ober)?|[Nn]ov(?:ember)?|[Dd]e(?:c|z)(?:ember)?)\b) "
            r"((?>\d\d){1,2}) ((?!<[0-9])((?:2[0123]|[01]?[0-9])):((?:[0-5]"
            r"[0-9]))(?::((?:(?:[0-5]?[0-9]|60)(?:[:.,][0-9]+)?)))(?![0-9])) "
            r"((?:Z|[+-]((?:2[0123]|[01]?[0-9]))(?::?((?:[0-5][0-9]))))))"
        )
        assert self.gph.compile(pattern_value=given) == expected
