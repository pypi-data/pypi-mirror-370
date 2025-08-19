from __future__ import annotations

from mu import loads


class Foo:
    pass


class Bar:
    def mu(self):
        return ["$yo!"]


class Baz:
    def mu(self):
        return ["x", "bla"]


def foobar():
    pass


class TestLoads:
    def test_jsox_load_atomic(self):
        assert loads(1) == 1
        assert loads(0.2) == 0.2
        assert loads("a") == "a"
        assert loads([]) == []
        assert loads(False) is False
        assert loads(None) is None

    def test_jsox_load_element(self):
        # Not sure if this should is None
        assert loads(["a"]) == []
        assert loads(["a", 10]) == 10
        assert loads(["a", 1, 2, 3]) == [1, 2, 3]

    def test_jsox_load_object(self):
        assert loads(["_", {"as": "object"}]) == {}

        assert loads(["_", {"as": "object"}, 10, 20, 30]) == {1: 10, 2: 20, 3: 30}

        assert loads(["_", {"as": "object"}, ["a", 10], ["b", 20], ["c", 30]]) == {
            "a": 10,
            "b": 20,
            "c": 30,
        }

        assert loads(
            [
                "_",
                {"as": "object"},
                ["a", 10, 11, 12],
                ["b", 20, 21, 22],
                ["c", 30, 31, 32],
            ]
        ) == {"a": [10, 11, 12], "b": [20, 21, 22], "c": [30, 31, 32]}

        assert loads(["_", {"as": "object"}, "x", "y", "z"]) == {1: "x", 2: "y", 3: "z"}

        assert loads(
            ["_", {"as": "object"}, ["a", "x", "y", "z"], ["b", "e", "f", "g"]]
        ) == {"a": ["x", "y", "z"], "b": ["e", "f", "g"]}

    def test_jsox_load_array(self):
        assert loads(["_", {"as": "array"}]) == []

        assert loads(["_", {"as": "array"}, 10, 20, 30]) == [10, 20, 30]

        assert loads(["_", {"as": "array"}, ["_", 10], ["_", 20], ["_", 30]]) == [
            10,
            20,
            30,
        ]

        assert loads(
            [
                "_",
                {"as": "array"},
                ["_", 10, 11, 12],
                ["_", 20, 21, 22],
                ["_", 30, 31, 32],
            ]
        ) == [[10, 11, 12], [20, 21, 22], [30, 31, 32]]

    def test_jsox_load_bool(self):
        assert loads(["_", {"as": "boolean", "value": "true()"}]) is True
        assert loads(["_", {"as": "boolean", "value": "false()"}]) is False

    def test_jsox_load_none(self):
        assert loads(["_", {"as": "null"}]) is None

        # ??? raise ValueError when there is a value? or just ignore
        assert loads(["_", {"as": "null"}, 1, 2, 3]) is None

    def test_jsox_load_array_one_item(self):
        assert loads(["_", {"as": "array"}, ["_", {"as": "object"}, ["a", 1]]]) == [
            {"a": 1}
        ]
