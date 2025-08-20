import pytest

from copious.data_structure.set import find_consecutive_subsets


@pytest.mark.parametrize("numbers, expected_output", [
    (set(), []),
    ({5}, [[5]]),
    ({2, 5, 8, 10}, [[2], [5], [8], [10]]),
    ({1, 2, 3, 4, 5}, [[1, 2, 3, 4, 5]]),
    ({4, 1, 8, 7, 9, 0}, [[0, 1], [4], [7, 8, 9]]),
    ({4, 1, 8, 7, 9, 0, 1, 2}, [[0, 1, 2], [4], [7, 8, 9]]),
    ({i for i in range(100)}, [[i for i in range(100)]])
])
def test_consecutive_subsets(numbers, expected_output):
    assert find_consecutive_subsets(numbers) == expected_output
