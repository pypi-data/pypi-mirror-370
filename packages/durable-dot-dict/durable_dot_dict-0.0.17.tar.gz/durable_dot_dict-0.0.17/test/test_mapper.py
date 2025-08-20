from durable_dot_dict.dot import Dot
from durable_dot_dict.dotdict import DotDict


def test_mapper_left1():
    data = DotDict() << {
        "b.a": None,
        'c.a': 1,
        'd.a': "",
        'e.a': {"b": 1},
        'f.a': [{"a": 1}, 1],
        "list": [1],
        "set": set()
    }

    assert Dot(data).b.a is None

    data.map({
        "ala_ma_kota": "test"
    }) << [
        ("b.a", 'ala_ma_kota'),
        ("d.a", 'none_existent')
    ]

    assert Dot(data).b.a == "test"
    assert Dot(data).d.a == ""


def test_mapper_left2():
    data = DotDict() << {
        "b.a": None,
        'c.a': 1,
        'd.a': "",
        'e.a': {"b": 1},
        'f.a': [{"a": 1}, 1],
        "list": [1],
        "set": set()
    }

    assert Dot(data).b.a is None

    data.map({
        "ala_ma_kota": "test"
    }) << {
        "b.a": 'ala_ma_kota',
        "d.a": 'none_existent'
    }

    assert Dot(data).b.a == "test"
    assert Dot(data).d.a == ""


def test_mapper_right1():
    data = DotDict() << {
        "b.a": None,
        'c.a': 1,
        'd.a': "",
        'e.a': {"b": 1},
        'f.a': [{"a": 1}, 1],
        "list": [1],
        "set": set()
    }

    assert Dot(data).b.a is None

    new_value = data.map({"ala_ma_kota": "test"}) >> [('none', 'a'), ('b', 'b'), ('c.a', 'c')]

    assert new_value == {'ala_ma_kota': 'test', 'b': {'a': None}, 'c': 1}


def test_mapper_right2():
    data = DotDict() << {
        "b.a": None,
        'c.a': 1,
        'd.a': "",
        'e.a': {"b": 1},
        'f.a': [{"a": 1}, 1],
        "list": [1],
        "set": set()
    }

    assert Dot(data).b.a is None

    # Use set to map

    new_value = data.map({"ala_ma_kota": "test"}) >> {"b.a", "c.a"}

    assert new_value == {'ala_ma_kota': 'test', 'b': {'a': None}, 'c': {"a": 1}}
