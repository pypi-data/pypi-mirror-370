from __future__ import annotations

from mu import dumps


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


class TestDumps:
    def test_jsox_dump_atomic(self):
        assert dumps(10) == ["_", {"as": "integer"}, 10]
        assert dumps(10) == ["_", {"as": "integer"}, 10]

    def test_jsox_dump_object(self):
        assert dumps({"x": 10}) == ["_", {"as": "object"}, ["x", {"as": "integer"}, 10]]

        assert dumps({"x": 10, "y": "abc"}) == [
            "_",
            {"as": "object"},
            ["x", {"as": "integer"}, 10],
            ["y", "abc"],
        ]

        assert dumps({"x": 10, "y": True}) == [
            "_",
            {"as": "object"},
            ["x", {"as": "integer"}, 10],
            ["y", {"as": "boolean", "value": "true()"}],
        ]

    def test_jsox_dump_array(self):
        assert dumps([1, 2, 3]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "integer"}, 2],
            ["_", {"as": "integer"}, 3],
        ]

        assert dumps([1, "2", False]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", "2"],
            ["_", {"as": "boolean", "value": "false()"}],
        ]

    def test_jsox_dump_nested(self):
        assert dumps([1, [2, 3, True], 4]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            [
                "_",
                {"as": "array"},
                ["_", {"as": "integer"}, 2],
                ["_", {"as": "integer"}, 3],
                ["_", {"as": "boolean", "value": "true()"}],
            ],
            ["_", {"as": "integer"}, 4],
        ]

        # not sure what to do with this. It's a valid data structure but already Mu form
        # what to do with attribute values?

        assert dumps(
            ["x", ["y", ["z", {"id": ("a", "b", "c"), "class": "foo"}, 1, 2, 3]]]
        ) == [
            "_",
            {"as": "array"},
            ["_", "x"],
            [
                "_",
                {"as": "array"},
                ["_", "y"],
                [
                    "_",
                    {"as": "array"},
                    ["_", "z"],
                    [
                        "_",
                        {"as": "object"},
                        ["id", {"as": "array"}, ["_", "a"], ["_", "b"], ["_", "c"]],
                        ["class", "foo"],
                    ],
                    ["_", {"as": "integer"}, 1],
                    ["_", {"as": "integer"}, 2],
                    ["_", {"as": "integer"}, 3],
                ],
            ],
        ]

    def test_jsox_dump_classes(self):
        assert dumps(Foo()) == ["_", {"as": "null"}]

        assert dumps(Bar()) == ["_", {"as": "mu"}, ["$yo!"]]

        assert dumps({"a": Foo(), "b": Bar()}) == [
            "_",
            {"as": "object"},
            ["a", {"as": "null"}],
            ["b", {"as": "mu"}, ["$yo!"]],
        ]

    def test_jsox_dump_xml_object(self):
        assert dumps(Baz()) == ["_", {"as": "mu"}, ["x", "bla"]]

    def test_jsox_dump_functions(self):
        assert dumps(foobar) == ["_", {"as": "null"}]

    def test_jsox_dump_none(self):
        assert dumps([1, None]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "null"}],
        ]

    def test_jsox_dump_empty_array(self):
        assert dumps([1, []]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "array"}],
        ]

    def test_jsox_dump_emtpy_dict(self):
        assert dumps([1, {}]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "object"}],
        ]

    def test_jsox_dump_float(self):
        assert dumps([1, 1.0]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "float"}, 1.0],
        ]

    def test_jsox_dump_complex(self):
        # not sure how to represent complex numbers in Mu

        assert dumps([1, 1j]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "complex"}, 1j],
        ]
