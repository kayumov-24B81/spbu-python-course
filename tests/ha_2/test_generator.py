import pytest
from project.ha_2.generator import *


@pytest.mark.parametrize(
    "data,expected",
    [
        ([1, 2, 3], [1, 2, 3]),
        ((1, 2, 3), [1, 2, 3]),
        ({1, 2, 3}, [1, 2, 3]),
        ("hello", ["hello"]),
        (b"abc", [b"abc"]),
        (42, [42]),
        (None, [None]),
        ([], []),
    ],
)
def test_generator_basic(data, expected):
    result = list(generator(data))

    if isinstance(data, set):
        assert set(result) == set(expected)
    else:
        assert result == expected


@pytest.mark.parametrize(
    "data, operations, expected",
    [
        ([1, 2, 3], [(map, lambda x: x * 2)], [2, 4, 6]),
        (
            [1, 2, 3, 4],
            [(filter, lambda x: x > 1), (map, lambda x: x * 10)],
            [20, 30, 40],
        ),
        (
            ["a", "bb", "ccc"],
            [(filter, lambda x: len(x) > 1), (map, str.upper)],
            ["BB", "CCC"],
        ),
    ],
)
def test_generator_integrated(data, operations, expected):
    result = collect(pipeline(generator(data), *operations), list)
    assert result == expected


def test_generator_lazy_iteration():
    gen = generator([1, 2, 3])

    assert next(gen) == 1
    assert next(gen) == 2
    assert next(gen) == 3

    with pytest.raises(StopIteration):
        next(gen)
