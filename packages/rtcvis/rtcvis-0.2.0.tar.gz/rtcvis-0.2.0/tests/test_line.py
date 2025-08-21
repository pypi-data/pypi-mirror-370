import pytest

from rtcvis.exceptions import ValidationException
from rtcvis.line import Line, line_intersection
from rtcvis.point import Point


@pytest.mark.parametrize(
    "a,b,e_a,e_b,e_is_vertical,e_slope",
    [
        # Check that init works with both Points and Tuples
        ((0, 0), (1, 0), (0, 0), (1, 0), False, 0),
        ((0, 0), Point(1, 0), (0, 0), (1, 0), False, 0),
        (Point(0, 0), (1, 0), (0, 0), (1, 0), False, 0),
        (Point(0, 0), Point(1, 0), (0, 0), (1, 0), False, 0),
        # a slope that's not 0
        ((0, 0), (1, 1), (0, 0), (1, 1), False, 1),
        # Swapped points
        ((1, 0), (0, 0), (0, 0), (1, 0), False, 0),
        # vertical line
        ((0, 0), (0, 1), (0, 0), (0, 1), True, None),
    ],
)
def test_init(a, b, e_a, e_b, e_is_vertical, e_slope):
    # construct the line
    line = Line(a, b)
    assert line.a == Point(*e_a)
    assert line.b == Point(*e_b)
    assert line.is_vertical == e_is_vertical
    assert line.slope == e_slope


def test_init_invalid():
    # Check that lines can't be created from identical Points
    with pytest.raises(ValidationException):
        Line((3, 3), (3, 3))


@pytest.mark.parametrize(
    "a,b,expected",
    [
        # normal line intersections
        (((0, 0), (1, 1)), ((0, 1), (1, 0)), (0.5, 0.5)),
        (((0, 0), (1, 1)), ((1, 1), (2, 0)), (1, 1)),
        (((-1, -1), (1, 0)), ((2, 4), (4, -2)), (3, 1)),
        # first and second point swapped
        (((1, 0), (-1, -1)), ((2, 4), (4, -2)), (3, 1)),
        # parallel lines, both identical and different
        (((0, 0), (1, 0)), ((5, 6), (3, 6)), None),
        (((0, 0), (1, 0)), ((0, 0), (1, 0)), None),
        (((0, 0), (1, 0)), ((-1, 0), (3, 0)), None),
        # two vertical lines, both identical and different
        (((0, 0), (0, -5)), ((0, 0), (0, -5)), None),
        (((0, 0), (0, -5)), ((0, -1), (0, 3)), None),
        (((0, 0), (0, -5)), ((2, -1), (2, 3)), None),
        # one vertical line, one non-vertical line
        (((0, 0), (0, -5)), ((-1, 0), (1, 1)), (0, 0.5)),
        (((0, 0), (0, -5)), ((-1, 0), (1, 0)), (0, 0)),
    ],
)
def test_line_intersection(a, b, expected):
    line_a = Line(*a)
    line_b = Line(*b)
    result = line_intersection(line_a, line_b)
    assert result == expected
