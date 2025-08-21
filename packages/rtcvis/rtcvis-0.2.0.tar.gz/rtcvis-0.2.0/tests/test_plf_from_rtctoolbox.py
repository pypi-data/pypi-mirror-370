import pytest

from rtcvis import PLF
from rtcvis.exceptions import ValidationException


@pytest.mark.parametrize(
    "points,x_end,expected",
    [
        # empty PLF
        ([], 33, PLF([])),
        # just one line
        ([(0, 0, 1)], 5, PLF([(0, 0), (5, 5)])),
        # just one pont
        ([(3, 4, 99)], 3, PLF([(3, 4)])),
        # several disconnected lines
        (
            [(0, 0, 1), (1.5, 0, 0), (2, 1, -1)],
            3,
            PLF([(0, 0), (1.5, 1.5), (1.5, 0), (2, 0), (2, 1), (3, 0)]),
        ),
        # discontinuities at start and end
        (
            [(0, 3, -1), (0, 1, 1), (3, 4, 6), (4, 0, 1)],
            4,
            PLF([(0, 3), (0, 1), (3, 4), (4, 10), (4, 0)]),
        ),
        # several connected lines
        (
            [(0, 0, 1), (3, 3, 1), (5, 5, 0), (7, 5, -1), (13, -1, 0)],
            15,
            PLF([(0, 0), (3, 3), (5, 5), (7, 5), (13, -1), (15, -1)]),
        ),
        # x_end defined before last point
        (
            [(0, 0, 2), (6, 0, 5)],
            4,
            PLF([(0, 0), (4, 8)]),
        ),
        # x_end defined before first point
        (
            [(0, 0, 1), (2, 3, 4)],
            -3,
            PLF([]),
        ),
    ],
)
def test_from_rtctoolbox(
    points: list[tuple[float, float, float]], x_end: float, expected: PLF
):
    result = PLF.from_rtctoolbox(points, x_end)
    assert result == expected


@pytest.mark.parametrize(
    "points,x_end",
    [
        ([(0, 0, 0), (-1, 0, 0)], 5),
        ([(0, 0, 0), (1, 3, 1), (1, 2, 4)], 9),
    ],
)
def test_from_rtctoolbox_invalid(
    points: list[tuple[float, float, float]], x_end: float
):
    with pytest.raises(ValidationException):
        PLF.from_rtctoolbox(points, x_end)
