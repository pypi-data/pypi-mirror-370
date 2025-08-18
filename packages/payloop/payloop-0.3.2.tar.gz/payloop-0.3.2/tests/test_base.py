from unit_test_objects import UnitTestX, UnitTestY

from payloop._base import BaseInvoke
from payloop._config import Config


def test_list_to_json_native_types():
    assert BaseInvoke(Config(), "abc").list_to_json([1, 2, 3]) == [1, 2, 3]

    assert BaseInvoke(Config(), "abc").list_to_json([{"a": "b"}, {"c": "d"}]) == [
        {"a": "b"},
        {"c": "d"},
    ]

    assert BaseInvoke(Config(), "abc").list_to_json([[1, 2], [3, 4], [{"a", "b"}]]) == [
        [1, 2],
        [3, 4],
        [{"a", "b"}],
    ]

    assert BaseInvoke(Config(), "abc").list_to_json(
        [[1, {"a": "b"}], [{"c": "d"}, 2]]
    ) == [
        [1, {"a": "b"}],
        [{"c": "d"}, 2],
    ]


def test_list_to_json_object_simple():
    assert BaseInvoke(Config(), "abc").list_to_json([1, UnitTestX()]) == [
        1,
        {"a": 1, "b": 2},
    ]


def test_list_to_json_object_complex():
    assert BaseInvoke(Config(), "abc").list_to_json([1, UnitTestY()]) == [
        1,
        {"c": 3, "d": {"a": 1, "b": 2}},
    ]


def test_list_to_json_list_list_list():
    assert BaseInvoke(Config(), "abc").list_to_json([1, [2, [3, [4]]]]) == [
        1,
        [2, [3, [4]]],
    ]


def test_list_to_dict_to_list():
    assert BaseInvoke(Config(), "abc").list_to_json([{"a": 1, "b": [1, [2]]}]) == [
        {"a": 1, "b": [1, [2]]}
    ]


def test_dict_to_json_dict():
    assert BaseInvoke(Config(), "abc").dict_to_json({"a": "b", "c": "d"}) == {
        "a": "b",
        "c": "d",
    }


def test_dist_to_json_dict_has_dict():
    assert BaseInvoke(Config(), "abc").dict_to_json(
        {"a": {"b": {"c": "d"}, "e": 123}}
    ) == {"a": {"b": {"c": "d"}, "e": 123}}
