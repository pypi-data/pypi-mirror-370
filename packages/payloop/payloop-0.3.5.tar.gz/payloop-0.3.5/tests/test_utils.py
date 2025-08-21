from payloop._utils import merge_chunk


def test_merge_chunk():
    merged = merge_chunk({}, {"a": 1, "b": [1, 2], "c": {"x": "foo"}})
    merged = merge_chunk(merged, {"b": [3], "c": {"y": "bar"}, "d": 5})
    merged = merge_chunk(merged, {"a": 2, "c": {"x": "baz"}})

    assert merged == {"a": 2, "b": [1, 2, 3], "c": {"x": "baz", "y": "bar"}, "d": 5}
