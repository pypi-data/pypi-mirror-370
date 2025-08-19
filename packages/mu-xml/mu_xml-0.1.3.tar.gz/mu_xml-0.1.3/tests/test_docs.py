# Tests from README.md
from __future__ import annotations

import mu
from mu import expand
from mu import Node
from mu import xml


class UL(Node):
    def __init__(self, **attrs):
        super().__init__("ul", **attrs)

    def __call__(self, *nodes, **attrs):
        nodes = [["li", node] for node in nodes]
        return super().__call__(*nodes, **attrs)


class TestReadMe:
    def test_usage(self):
        assert (
            xml(["p", "Hello, ", ["b", "World"], "!"]) == "<p>Hello, <b>World</b>!</p>"
        )

    def test_element_nodes(self):
        el = ["p", {"id": 1}, "this is a paragraph."]
        assert mu.tag(el) == "p"
        assert mu.attrs(el) == {"id": 1}
        assert mu.content(el) == ["this is a paragraph."]
        assert mu.get_attr("id", el) == 1
        assert xml(el) == '<p id="1">this is a paragraph.</p>'
        assert mu.is_element(el) is True
        assert mu.is_special_node(el) is False
        assert mu.is_empty(el) is False
        assert mu.has_attrs(el) is True

    def test_special_nodes(self):
        assert xml(["$comment", "this is a comment"]) == "<!-- this is a comment -->"
        assert xml(["$pi", "foo", "bar"]) == "<?foo bar?>"
        assert xml(["$cdata", "<foo>"]) == "<![CDATA[<foo>]]>"
        assert xml(["$raw", "<foo/>"]) == "<foo/>"
        assert xml(["$text", "<foo>"]) == "&lt;foo&gt;"

    def test_namespaces(self):
        assert (
            xml(
                [
                    "svg",
                    dict(xmlns="http://www.w3.org/2000/svg"),
                    ["rect", dict(width=200, height=100, x=10, y=10)],
                ]
            )
            == '<svg xmlns="http://www.w3.org/2000/svg"><rect height="100" width="200" x="10" y="10"/></svg>'  # noqa
        )

        assert (
            xml(
                [
                    "svg:svg",
                    {"xmlns:svg": "http://www.w3.org/2000/svg"},
                    ["svg:rect", {"width": 200, "height": 100, "x": 10, "y": 10}],
                ]
            )
            == '<svg:svg xmlns:svg="http://www.w3.org/2000/svg"><svg:rect height="100" width="200" x="10" y="10"/></svg:svg>'  # noqa
        )

    def test_object_nodes(self):
        assert xml(["div", UL(), "foo"]) == "<div><ul/>foo</div>"
        assert (
            xml(
                ["div", [UL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]]
            )
            == '<div><ul class="foo bar"><li>item 1</li><li>item 2</li><li>item 3</li></ul></div>'  # noqa
        )
        assert (
            xml(["div", [UL(id=1, cls=("foo", "bar")), "item 1", "item 2", "item 3"]])
            == '<div><ul class="foo bar" id="1"><li>item 1</li><li>item 2</li><li>item 3</li></ul></div>'  # noqa
        )

    def test_expand(self):
        assert expand(
            ["div", [UL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]]
        ) == [
            "div",
            [
                "ul",
                {"class": ("foo", "bar")},
                ["li", "item 1"],
                ["li", "item 2"],
                ["li", "item 3"],
            ],
        ]

    def test_extra(self):
        assert xml(["$comment", "a", "--", "b"]) == "<!-- a&#8208;&#8208;b -->"
