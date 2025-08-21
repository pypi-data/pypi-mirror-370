import pytest

from rtcvis import PLF, Point


@pytest.mark.parametrize(
    "plf,e_min,e_max",
    [
        (PLF([(0, 0), (1, 1)]), Point(0, 0), Point(1, 1)),
        (PLF([(-5, -1), (1, 1), (1, -1.5), (30, 1.1)]), Point(1, -1.5), Point(30, 1.1)),
    ],
)
def test_plf_extrema(plf, e_min, e_max):
    assert plf.min == e_min
    assert plf.max == e_max
