from __future__ import annotations

from mu import expand
from mu import Node


class TestExpand:
    def test_expand_mu(self):
        # mu without any extra stuff should just reproduce the
        # same structure with None removed.
        assert expand([]) == []
        assert expand([1, 2, 3]) == [1, 2, 3]
        assert expand([1, None, 2, None, 3]) == [1, 2, 3]
        assert expand([(1), 2, (3)]) == [1, 2, 3]
        assert expand(["foo", {}, "bar"]) == ["foo", "bar"]

    def test_expand_no_sugar(self):
        assert expand(["p.foo#bar", "baz"]) == ["p.foo#bar", "baz"]


class UL(Node):
    def __init__(self, **attrs):
        super().__init__("ul", **attrs)

    def __call__(self, *nodes, **attrs):
        nodes = [["li", node] for node in nodes]
        return super().__call__(*nodes, **attrs)


class TestExpandActiveNode:
    def test_active_element(self):
        assert expand(["div", [UL(cls="foo"), 1, 2, 3]]) == [
            "div",
            [
                "ul",
                {"class": "foo"},
                ["li", 1],
                ["li", 2],
                ["li", 3],
            ],
        ]

    def test_nested_active_elements(self):
        assert expand(["div", [UL(cls="foo"), 1, 2, [UL(cls="bar"), 3, 4]]]) == [
            "div",
            [
                "ul",
                {"class": "foo"},
                ["li", 1],
                ["li", 2],
                [
                    "li",
                    [
                        "ul",
                        {"class": "bar"},
                        ["li", 3],
                        ["li", 4],
                    ],
                ],
            ],
        ]
