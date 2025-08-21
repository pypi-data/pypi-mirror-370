import pytest

from rtcvis import PLF


@pytest.mark.parametrize(
    "plf,mirror,offset,expected",
    [
        (
            PLF([(0, 0), (1, 1)]),
            True,
            1,
            PLF([(0, 1), (1, 0)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            False,
            -0.5,
            PLF([(-0.5, 0), (0.5, 1)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            True,
            0.5,
            PLF([(-0.5, 1), (0.5, 0)]),
        ),
        (
            PLF([(0, 1), (1, 1)]),
            True,
            0.5,
            PLF([(-0.5, 1), (0.5, 1)]),
        ),
        (
            PLF([(0, 1), (3, 2.5), (4, 3), (8, 4)]),
            True,
            3.5,
            PLF([(-4.5, 4), (-0.5, 3), (0.5, 2.5), (3.5, 1)]),
        ),
    ],
)
def test_plf_transformed(plf: PLF, mirror: bool, offset: float, expected: PLF):
    result = plf.transformed(mirror=mirror, offset=offset)
    assert result == expected
