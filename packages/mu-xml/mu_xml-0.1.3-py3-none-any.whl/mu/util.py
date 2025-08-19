from __future__ import annotations

import html


def escape_html(text):
    return html.escape(str(text))


def raw_string(text):
    return ["$raw", text]
