from __future__ import annotations

import pytest
from mu import _is_active_element
from mu import attrs
from mu import content
from mu import get_attr
from mu import has_attrs
from mu import html
from mu import is_element
from mu import is_empty
from mu import is_special_node
from mu import Node
from mu import tag
from mu import xml


class UL(Node):
    def __init__(self, **attrs):
        super().__init__("ul", **attrs)

    def __call__(self, *nodes, **attrs):
        nodes = [["li", node] for node in nodes]
        return super().__call__(*nodes, **attrs)


class TestTagNames:
    def test_basic_tags(self):
        assert xml(["div"]) == "<div/>"

    def test_tag_syntax_sugar(self):
        assert xml(["div#foo"]) == '<div id="foo"/>'
        assert xml(["div.foo"]) == '<div class="foo"/>'
        assert xml(["div.foo", "bar", "baz"]) == '<div class="foo">barbaz</div>'
        assert xml(["div.a.b"]) == '<div class="a b"/>'
        assert xml(["div#foo.bar.baz"]) == '<div class="bar baz" id="foo"/>'


class TestAccessors:
    def test_tag(self):
        assert tag(["foo"]) == "foo"
        assert tag(["$foo"]) == "$foo"

    def test_no_attrs(self):
        assert attrs(["foo"]) == {}
        assert attrs(["foo", {}]) == {}
        assert attrs(["foo", "bla", {"a": 10}]) == {}

    def test_attrs(self):
        assert attrs(["foo", {"a": 10, "b": 20}]) == {"a": 10, "b": 20}

    def test_content(self):
        assert content(["foo", "bar", "baz"]) == ["bar", "baz"]
        assert content(["foo"]) == []
        assert content(["foo", {}]) == []
        assert content(["foo", "bar"]) == ["bar"]


class TestNotElement:
    def test_tag(self):
        with pytest.raises(ValueError):
            assert tag(None) is None
        with pytest.raises(ValueError):
            assert tag(0) is None
        with pytest.raises(ValueError):
            assert tag([]) is None
        with pytest.raises(ValueError):
            assert tag({}) is None


class TestIsElement:
    def test_is_not_element(self):
        assert is_element([]) is False
        assert is_element(0) is False
        assert is_element(None) is False
        assert is_element({}) is False
        assert is_element("foo") is False
        assert is_element(True) is False

    def test_is_element(self):
        assert is_element(["foo"]) is True
        assert is_element(["foo", ["bar"]]) is True
        assert is_element(["foo", "bla"]) is True
        assert is_element(["foo", {}, "bla"]) is True

    def test_is_not_active_element(self):
        assert _is_active_element([bool, 1, 2, 3]) is False

    def test_is_active_element(self):
        assert is_element(UL()) is False
        assert is_element([UL()]) is True
        assert is_element([UL(), 1]) is True
        assert is_element([UL(), {}, 1]) is True
        assert is_element([UL(cls="foo"), 1, 2, 3]) is True


class TestIsSpecialNode:
    def test_is_not_special(self):
        assert is_special_node(None) is False
        assert is_special_node("foo") is False
        assert is_special_node([]) is False
        assert is_special_node(["foo"]) is False

    def test_is_special(self):
        assert is_special_node(["$comment"]) is True
        assert is_special_node(["$cdata"]) is True
        assert is_special_node(["$pi"]) is True
        assert is_special_node(["$foo"]) is True
        assert is_special_node(["$raw"]) is True


class TestHasAttributes:
    # FIXME URL values should be handled differently
    def test_has_not(self):
        assert has_attrs(None) is False
        assert has_attrs("foo") is False
        assert has_attrs([]) is False
        assert has_attrs(["foo"]) is False
        assert has_attrs(["foo", {}]) is False
        assert has_attrs(["foo", "bla", {"a": 10}]) is False

    def test_has(self):
        assert has_attrs(["foo", {"a": 10, "b": 20}]) is True
        assert has_attrs(["foo", {"a": 10, "b": 20}, "bla"]) is True


class TestIsEmpty:
    def test_is_empty(self):
        assert is_empty("foo") is False
        assert is_empty(["foo"]) is True
        assert is_empty(["foo", {}]) is True
        assert is_empty(["foo", (1, 2, 3)]) is False


class TestGetAttr:
    def test_get_attr(self):
        assert get_attr("a", ["x", {"a": 10}]) == 10
        assert get_attr("a", ["x", {"b": 10}], 20) == 20
        with pytest.raises(ValueError):
            get_attr("a", "x", 20)
