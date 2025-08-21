import pytest

from rtcvis import PLF
from rtcvis.plf import plf_merge


@pytest.mark.parametrize(
    "a, b, expected",
    [
        # Trivial cases
        (
            PLF([]),
            PLF([]),
            PLF([]),
        ),
        (
            PLF([]),
            PLF([(1, 1)]),
            PLF([(1, 1)]),
        ),
        (
            PLF([(1, 1)]),
            PLF([]),
            PLF([(1, 1)]),
        ),
        # b is defined before and after a
        (
            PLF([(0, 0), (1, 0)]),
            PLF([(-1, 1), (2, 1)]),
            PLF([(-1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (2, 1)]),
        ),
        # a has a redundant point at the end
        (
            PLF([(0, 0), (1, 0), (1, 10)]),
            PLF([(-1, 1), (2, 1)]),
            PLF([(-1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (2, 1)]),
        ),
        # a and b start and end at the same x
        (
            PLF([(0, 0), (1, 0)]),
            PLF([(0, 0), (1, 1)]),
            PLF([(0, 0), (1, 0)]),
        ),
    ],
)
def test_plf_merge(a: PLF, b: PLF, expected: PLF):
    result = plf_merge(a, b)
    assert result == expected
