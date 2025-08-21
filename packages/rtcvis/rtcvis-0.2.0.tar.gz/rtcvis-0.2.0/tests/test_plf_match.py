import pytest

from rtcvis import PLF
from rtcvis.plf import match_plf


@pytest.mark.parametrize(
    "a,b,e_a,e_b",
    [
        # shouldn't modify b
        (
            PLF([(0, 0), (2, 2)]),
            PLF([(0, 0), (1, 0.5), (2, 2.5)]),
            PLF([(0, 0), (1, 1), (2, 2)]),
            PLF([(0, 0), (1, 0.5), (2, 2.5)]),
        ),
        # shouldn't modify a
        (
            PLF([(0, 0), (1, 1), (1, 0), (2, 1)]),
            PLF([(0, 1), (2, 3)]),
            PLF([(0, 0), (1, 1), (1, 0), (2, 1)]),
            PLF([(0, 1), (1, 2), (1, 2), (2, 3)]),
        ),
        # "normal" PLFs
        (
            PLF([(0, 1), (4, 5), (8, 4)]),
            PLF([(0, 2), (2, 0), (5, 1), (8, -2)]),
            PLF([(0, 1), (2, 3), (4, 5), (5, 4.75), (8, 4)]),
            PLF([(0, 2), (2, 0), (4, 2 / 3), (5, 1), (8, -2)]),
        ),
        # match a PLF with itself
        (
            PLF([(0, 2), (2, 0), (5, 1), (8, -2)]),
            PLF([(0, 2), (2, 0), (5, 1), (8, -2)]),
            PLF([(0, 2), (2, 0), (5, 1), (8, -2)]),
            PLF([(0, 2), (2, 0), (5, 1), (8, -2)]),
        ),
        # match with an empty PLF
        (
            PLF([]),
            PLF([(0, 0)]),
            PLF([]),
            PLF([]),
        ),
        # match empty PLF with itself
        (
            PLF([]),
            PLF([]),
            PLF([]),
            PLF([]),
        ),
        # non-overlapping
        (
            PLF([(3, -1)]),
            PLF([(-2, 5)]),
            PLF([]),
            PLF([]),
        ),
        # PLFs with just 1 point each
        (
            PLF([(-2, -1)]),
            PLF([(-2, 5)]),
            PLF([(-2, -1)]),
            PLF([(-2, 5)]),
        ),
        # one PLF has just 1 point
        (
            PLF([(-2, -1)]),
            PLF([(-3, 5), (-1, 6)]),
            PLF([(-2, -1)]),
            PLF([(-2, 5.5)]),
        ),
        # normal PLF
        (
            PLF([(-1, 0), (1, 0)]),
            PLF([(-2, 1), (0, 0), (2, 1)]),
            PLF([(-1, 0), (0, 0), (1, 0)]),
            PLF([(-1, 0.5), (0, 0), (1, 0.5)]),
        ),
        # one PLF has a discontinuity in the middle
        (
            PLF([(-1, 0), (0, 0), (0, 1), (1, 1)]),
            PLF([(-0.5, 0), (1.5, 2)]),
            PLF([(-0.5, 0), (0, 0), (0, 1), (1, 1)]),
            PLF([(-0.5, 0), (0, 0.5), (0, 0.5), (1, 1.5)]),
        ),
        # one PLF has a discontinuity at the end
        (
            PLF([(0, 0), (4, 2), (4, 0)]),
            PLF([(0, 0), (4, 3)]),
            PLF([(0, 0), (4, 2), (4, 0)]),
            PLF([(0, 0), (4, 3), (4, 3)]),
        ),
        # one PLF with a discontinuity, the other one is just a Point
        (
            PLF([(0, 0)]),
            PLF([(0, 0), (0, 1)]),
            PLF([(0, 0), (0, 0)]),
            PLF([(0, 0), (0, 1)]),
        ),
        # a is just a point, b is two identical points
        (
            PLF([(0, 0)]),
            PLF([(0, 0), (0, 0)]),
            PLF([(0, 0), (0, 0)]),
            PLF([(0, 0), (0, 0)]),
        ),
        # both PLFs have a discontinuity at the same spot
        (
            PLF([(0, 1), (0.5, 0), (1, 0), (1, 1)]),
            PLF([(0, 0), (1, 0), (1, -1)]),
            PLF([(0, 1), (0.5, 0), (1, 0), (1, 1)]),
            PLF([(0, 0), (0.5, 0), (1, 0), (1, -1)]),
        ),
        # a has a duplicate point in the middle
        (
            PLF([(0, 1), (0.5, 0), (0.5, 0), (1, 1)]),
            PLF([(0, 0), (1, 0)]),
            PLF([(0, 1), (0.5, 0), (0.5, 0), (1, 1)]),
            PLF([(0, 0), (0.5, 0), (0.5, 0), (1, 0)]),
        ),
        # a has a duplicate point in the middle and b has a single point there
        (
            PLF([(0, 1), (0.5, 0), (0.5, 0), (1, 1)]),
            PLF([(0, 0), (0.5, 0), (1, 0)]),
            PLF([(0, 1), (0.5, 0), (0.5, 0), (1, 1)]),
            PLF([(0, 0), (0.5, 0), (0.5, 0), (1, 0)]),
        ),
    ],
)
def test_plf_match(a: PLF, b: PLF, e_a: PLF, e_b: PLF):
    result_a, result_b = match_plf(a, b)
    assert result_a == e_a
    assert result_b == e_b
