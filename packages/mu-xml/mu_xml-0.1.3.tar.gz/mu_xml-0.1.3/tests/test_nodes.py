from __future__ import annotations

from mu import CData
from mu import Comment
from mu import Element
from mu import expand
from mu import Node
from mu import PI
from mu import Raw
from mu import Text


class TestElement:
    def test_element(self):
        el = Element("p")
        assert el.tag == "p"
        assert el.attrs == {}
        assert el.content == []
        assert el() == ["p"]
        assert el("foo", "bar") == ["p", "foo", "bar"]

        el = Element("p", "foo", "bar")
        assert el.tag == "p"
        assert el.attrs == {}
        assert el.content == ["foo", "bar"]
        assert el() == ["p", "foo", "bar"]
        assert el(foo=10, bar=20) == [
            "p",
            {"foo": 10, "bar": 20},
            "foo",
            "bar",
        ]
        assert el("baz", foo=10, bar=20) == [
            "p",
            {"foo": 10, "bar": 20},
            "foo",
            "bar",
            "baz",
        ]

        el = Element("p", "foo", "bar", foo=10, bar=20)
        assert el.tag == "p"
        assert el.attrs == {"foo": 10, "bar": 20}
        assert el.content == ["foo", "bar"]
        assert el() == [
            "p",
            {"foo": 10, "bar": 20},
            "foo",
            "bar",
        ]
        assert el(foo=30) == [
            "p",
            {"foo": 30, "bar": 20},
            "foo",
            "bar",
        ]

    def test_class_attribute(self):
        el = Element("p", cls="foo")
        assert el.attrs == {"class": "foo"}
        assert hasattr(el.attrs, "cls") is False
        assert el(cls="bar") == ["p", {"class": "bar"}]


class TestText:
    def test_text_node(self):
        assert Text("foo", "bar")() == ["$text", "foo", "bar"]


class TestComment:
    def test_comment_node(self):
        assert Comment("foo", "bar")() == ["$comment", "foo", "bar"]


class TestPI:
    def test_pi_node(self):
        assert PI("foo", "bar")() == ["$pi", "foo", "bar"]


class TestCData:
    def test_cdata_node(self):
        assert CData("foo", "bar")() == ["$cdata", "foo", "bar"]


class TestRaw:
    def test_raw_node(self):
        assert Raw("foo", "bar")() == ["$raw", "foo", "bar"]


class UL(Node):
    def __init__(self, **attrs):
        super().__init__("ul", **attrs)

    def __call__(self, *nodes, **attrs):
        nodes = [["li", node] for node in nodes]
        return super().__call__(*nodes, **attrs)


class TestCustomNode:
    def test_custom_node(self):
        ul = UL(x=10)
        assert ul() == ["ul", {"x": 10}]
        assert ul(1, 2, 3) == [
            "ul",
            {"x": 10},
            ["li", 1],
            ["li", 2],
            ["li", 3],
        ]
        assert ul(1, 2, 3, cls="foo") == [
            "ul",
            {"x": 10, "class": "foo"},
            ["li", 1],
            ["li", 2],
            ["li", 3],
        ]

    def test_custom_node_in_elem_pos(self):
        div = ["div", [UL(cls="foo"), 1, 2, 3]]
        # div is a literal so use expand()
        assert expand(div) == [
            "div",
            [
                "ul",
                {"class": "foo"},
                ["li", 1],
                ["li", 2],
                ["li", 3],
            ],
        ]
