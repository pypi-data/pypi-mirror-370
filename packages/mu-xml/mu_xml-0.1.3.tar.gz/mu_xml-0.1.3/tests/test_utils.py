from __future__ import annotations

from mu.util import escape_html
from mu.util import raw_string

RAW = "!@#^$%&*()><?/`~"
RAW_ESCAPED = "!@#^$%&amp;*()&gt;&lt;?/`~"


class TestEscapeHTML:
    def test_escape_html(self):
        assert escape_html(RAW) == RAW_ESCAPED


class TestRawString:
    def test_raw_strings(self):
        assert raw_string(RAW) == ["$raw", RAW]
