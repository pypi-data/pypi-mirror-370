from copious.data_structure.list import flatten


def test_flatten():
    flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    flatten([[1, 2], [3, 4], [5]]) == [1, 2, 3, 4, 5]
    flatten([[1, 2], [], [5, 6]]) == [1, 2, 5, 6]
    flatten([[1, 2, 3]]) == [1, 2, 3]
    flatten([[]]) == []
    flatten([]) == []
