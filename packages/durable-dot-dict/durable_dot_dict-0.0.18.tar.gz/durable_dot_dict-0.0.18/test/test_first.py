from durable_dot_dict.collection import first, first_not_none


def test_first():
    a1 = {}
    a2 = {"b": 1}
    result = first(lambda: a1["a"], lambda: a2["b"])
    assert result == 1

def test_first_not_none():
    a1 = {}
    a2 = {"b": 1}
    result = first_not_none(lambda: a1["a"], lambda : None, lambda: a2["b"])
    assert result == 1