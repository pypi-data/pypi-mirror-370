from collections import defaultdict

from copious.data_structure.dict import defaultdict2dict


def test_simple_defaultdict():
    d = defaultdict(int)
    d["a"] = 1
    d["b"] = 2
    assert defaultdict2dict(d) == {"a": 1, "b": 2}


def test_nested_defaultdict():
    d = defaultdict(lambda: defaultdict(int))
    d["x"]["y"] = 10
    d["x"]["z"] = 20
    d["p"]["q"] = 30
    expected = {"x": {"y": 10, "z": 20}, "p": {"q": 30}}
    assert defaultdict2dict(d) == expected


def test_defaultdict_with_list():
    d = defaultdict(list)
    d["a"].append(1)
    d["a"].append(2)
    d["b"].append(3)
    assert defaultdict2dict(d) == {"a": [1, 2], "b": [3]}


def test_complex_nested_structure():
    d = defaultdict(lambda: defaultdict(list))
    d["x"]["y"].append(defaultdict(int, a=1, b=2))
    d["x"]["z"].append(3)
    d["p"]["q"].extend([4, 5, defaultdict(list)])
    expected = {"x": {"y": [{"a": 1, "b": 2}], "z": [3]}, "p": {"q": [4, 5, {}]}}
    assert defaultdict2dict(d) == expected


def test_empty_defaultdict():
    d = defaultdict(int)
    assert defaultdict2dict(d) == {}


def test_defaultdict_with_tuple():
    d = defaultdict(tuple)
    d["a"] = (1, 2, defaultdict(int, x=10))
    expected = {"a": (1, 2, {"x": 10})}
    assert defaultdict2dict(d) == expected
