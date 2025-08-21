import pytest

from rtcvis import PLF


@pytest.mark.parametrize(
    "plf,start,expected",
    [
        (
            PLF([(0, 0), (1, 1)]),
            0,
            PLF([(0, 0), (1, 1)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            -0.5,
            PLF([(0, 0), (1, 1)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            0.2,
            PLF([(0.2, 0.2), (1, 1)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            1,
            PLF([(1, 1)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            1.1,
            PLF([]),
        ),
    ],
)
def test_plf_start_truncated(plf: PLF, start: float, expected: PLF):
    result = plf.start_truncated(start)
    assert result == expected


@pytest.mark.parametrize(
    "plf,end,expected",
    [
        (
            PLF([(0, 0), (1, 1)]),
            0,
            PLF([(0, 0)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            -0.5,
            PLF([]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            0.2,
            PLF([(0, 0), (0.2, 0.2)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            1,
            PLF([(0, 0), (1, 1)]),
        ),
        (
            PLF([(0, 0), (1, 1)]),
            1.1,
            PLF([(0, 0), (1, 1)]),
        ),
    ],
)
def test_plf_end_truncated(plf: PLF, end: float, expected: PLF):
    result = plf.end_truncated(end)
    assert result == expected
