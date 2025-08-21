from durable_dot_dict.dot import DotList
from durable_dot_dict.dotdict import DotDict


def test_dot_list1():
    d1 = DotDict({
        "a": {
            "b": 1,
            "c": {
                "v1": [{"d": 2}],
                "v2": 1
            }
        }
    })
    d2 = DotDict({
        "a": {
            "c": [{"d": 123}]
        }
    })
    dot_list = DotList([d1, d2])
    flat = dot_list.flatten()
    assert isinstance(flat[0], dict)
    merged = dot_list.merge()
    # Data from d1 should remain
    assert merged['a.b'] == d1['a.b']
    assert merged['a.c.v1'] == d1['a.c.v1']
    assert merged['a.c.v2'] == d1['a.c.v2']

    # Added new for d2
    assert merged['a.c'] == d2['a.c']


def test_dot_list2():
    d1 = DotDict({
        "a": {
            "b": 1,
            "c": {
                "v1": [{"d": 2}],
                "v2": 1
            }
        }
    })
    d2 = DotDict({
        "a": {
            "c": {"d": 123, "v2": 123}
        }
    })
    dot_list = DotList([d1, d2])
    flat = dot_list.flatten()
    assert isinstance(flat[0], dict)
    merged = dot_list.merge()
    # Data from d1 should remain
    assert merged['a.b'] == d1['a.b']
    assert merged['a.c.v1'] == d1['a.c.v1']

    # Added new for d2
    assert merged['a.c.d'] == d2['a.c.d']
    assert merged['a.c.v2'] == d2['a.c.v2']


def test_dot_list_flatten():
    d1 = DotDict({
        "a": {
            "b": 1,
            "c": {
                "v1": [{"d": 2}],
                "v2": 1
            }
        }
    })
    d2 = DotDict({
        "a": {
            "c": {"d": 123, "v2": 123}
        }
    })
    dot_list = DotList([d1, d2])
    flat = dot_list.flatten(allow =['a.c.v2'])
    assert flat == [{'a.c.v2': 1}, {'a.c.v2': 123}]