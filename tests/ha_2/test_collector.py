import pytest
from project.ha_2.generator import *


@pytest.mark.parametrize(
    "data, type, expected",
    [
        ([0, 1, 2], list, [0, 1, 2]),
        ([0, 1, 2, 2], set, {0, 1, 2}),
        ([0, 1, 2], tuple, (0, 1, 2)),
        ([(0, 0), (1, 2), (2, 4)], dict, {0: 0, 1: 2, 2: 4}),
        ([], list, []),
    ],
)
def test_collector_types(data, type, expected):
    result = collect(pipeline(iter(data)), type)
    assert result == expected


def test_collector_integrated():

    result = pipeline(
        generator(range(10)),
        (filter, lambda x: x % 2 == 0),
        (map, lambda x: 3 * x),
        (enumerate, 1),
    )

    assert collect(result, list) == [(1, 0), (2, 6), (3, 12), (4, 18), (5, 24)]
