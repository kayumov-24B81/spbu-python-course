import pytest
from functools import reduce
from project.ha_2.generator import *


@pytest.mark.parametrize(
    "data, function, expected",
    [
        ([1, 2, 3], lambda x: 2 * x, [2, 4, 6]),
        (["a", "b"], lambda x: x.upper(), ["A", "B"]),
        ([1, 2, 3], str, ["1", "2", "3"]),
        ([], lambda x: 2 * x, []),
    ],
)
def test_map(data, function, expected):
    result = pipeline(iter(data), (map, function))
    assert list(result) == expected


@pytest.mark.parametrize(
    "data, function ,expected",
    [
        ([1, 2, 3, 4], lambda x: x % 2 == 0, [2, 4]),
        (["a", "bb", "ccc"], lambda x: len(x) > 1, ["bb", "ccc"]),
        ([0, 1, False, True], bool, [1, True]),
        ([1, 2, 3], lambda x: x > 5, []),
    ],
)
def test_filter(data, function, expected):
    result = pipeline(iter(data), (filter, function))
    assert list(result) == expected


@pytest.mark.parametrize(
    "data, second_data, expected",
    [
        ([1, 2, 3], [4, 5, 6], [(1, 4), (2, 5), (3, 6)]),
        ([1, 2, 3], ["a", "b", "c"], [(1, "a"), (2, "b"), (3, "c")]),
        ([], [], []),
    ],
)
def test_zip(data, second_data, expected):
    result = pipeline(iter(data), (zip, second_data))
    assert list(result) == expected


@pytest.mark.parametrize(
    "data, operation, expected",
    [
        ([1, 2, 3, 4], (reduce, lambda x, y: x + y, 0), 10),
        ([1, 2, 3, 4], (reduce, lambda x, y: x + y, 10), 20),
        ([1, 2, 3, 4], (reduce, lambda x, y: x * y, 1), 24),
        (["a", "b", "c"], (reduce, lambda x, y: x + y, ""), "abc"),
        ([1, 2, 3, 4], (reduce, lambda x, y: x + y), 10),
    ],
)
def test_reduce(data, operation, expected):
    result = pipeline(iter(data), operation)
    assert result == expected


def test_enum():
    result = pipeline(iter(["a", "b", "c"]), (enumerate, 1))
    assert list(result) == [(1, "a"), (2, "b"), (3, "c")]


@pytest.fixture
def number_gen():
    return generator([0, 1, 2, 3, 4])


@pytest.mark.parametrize(
    "operations, expected",
    [
        ([(map, lambda x: 2 * x), (filter, lambda x: x > 3)], [4, 6, 8]),
        (
            [(map, lambda x: x - 2), (zip, iter([0, 1, 2, 3, 4]))],
            [(-2, 0), (-1, 1), (0, 2), (1, 3), (2, 4)],
        ),
        ([(filter, lambda x: x % 2 == 0), (enumerate, 1)], [(1, 0), (2, 2), (3, 4)]),
    ],
)
def test_mix(number_gen, operations, expected):
    result = pipeline(number_gen, *operations)
    assert list(result) == expected


def test_reduce_mix(number_gen):
    result = pipeline(
        number_gen, (filter, lambda x: x > 2), (reduce, lambda x, y: x * y, 1)
    )
    assert 12 == result


def test_custom_operation():
    def split(stream, start_size=1):
        piece = []
        size = start_size
        for item in stream:
            piece.append(item)
            if len(piece) == size:
                yield piece
                piece = []
                size += 1
        if piece:
            yield piece

    result = pipeline(iter([1, 2, 3, 4, 5, 6]), split)
    assert list(result) == [[1], [2, 3], [4, 5, 6]]


def test_callable(number_gen):
    def custom_reduce(stream):
        return reduce(lambda x, y: 2 * (x + y), stream, 0)

    result = pipeline(number_gen, custom_reduce)
    assert result == 52
