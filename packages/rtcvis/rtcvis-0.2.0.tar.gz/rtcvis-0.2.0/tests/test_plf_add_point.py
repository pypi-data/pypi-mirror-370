import pytest

from rtcvis import PLF, Point


@pytest.mark.parametrize(
    "plf,p,expected",
    [
        (PLF([]), Point(3, 5), PLF([])),
        (PLF([(0, 0)]), Point(3, 5), PLF([(3, 5)])),
        (PLF([(-1, 4)]), Point(3, 5), PLF([(2, 9)])),
        (PLF([(-1, 2), (1, -2)]), Point(3, 5), PLF([(2, 7), (4, 3)])),
    ],
)
def test_add_point(plf: PLF, p: Point, expected: PLF):
    result = plf.add_point(other=p, subtract_x=False, subtract_y=False)
    assert result == expected


@pytest.mark.parametrize(
    "plf,p,expected",
    [
        (PLF([]), Point(3, 5), PLF([])),
        (PLF([(0, 0)]), Point(3, 5), PLF([(3, -5)])),
        (PLF([(-1, 4)]), Point(3, 5), PLF([(2, -1)])),
        (PLF([(-1, 2), (1, -2)]), Point(3, 5), PLF([(2, -3), (4, -7)])),
    ],
)
def test_add_point_ysub(plf: PLF, p: Point, expected: PLF):
    result = plf.add_point(other=p, subtract_x=False, subtract_y=True)
    assert result == expected


@pytest.mark.parametrize(
    "plf,p,expected",
    [
        (PLF([]), Point(3, 5), PLF([])),
        (PLF([(0, 0)]), Point(3, 5), PLF([(-3, 5)])),
        (PLF([(-1, 4)]), Point(3, 5), PLF([(-4, 9)])),
        (PLF([(-1, 2), (1, -2)]), Point(3, 5), PLF([(-4, 7), (-2, 3)])),
    ],
)
def test_add_point_xsub(plf: PLF, p: Point, expected: PLF):
    result = plf.add_point(other=p, subtract_x=True, subtract_y=False)
    assert result == expected
