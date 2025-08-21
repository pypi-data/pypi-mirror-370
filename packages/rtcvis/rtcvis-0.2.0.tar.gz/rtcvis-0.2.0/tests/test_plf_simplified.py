import pytest

from rtcvis import PLF


@pytest.mark.parametrize(
    "plf",
    [
        PLF([]),
        PLF([(0, 5)]),
        PLF([(0, 3), (2, 5)]),
        PLF([(0, 3), (0, 4)]),
        PLF([(1, 1), (2, 2), (3, 1)]),
        PLF([(1, 1), (2, 2), (2, 3)]),
        PLF([(0, 1), (0, 0), (1, 0)]),
    ],
)
def test_plf_simplified_unmodified(plf: PLF):
    simplified = plf.simplified()
    assert simplified == plf


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            PLF([(0, 0), (1, 0), (2, 0)]),
            PLF([(0, 0), (2, 0)]),
        ),
        (
            PLF([(0, 0), (1, 1), (2, 2)]),
            PLF([(0, 0), (2, 2)]),
        ),
        (
            PLF([(0, 0), (1, 1), (2, 2), (3, 3)]),
            PLF([(0, 0), (3, 3)]),
        ),
        (
            PLF(
                [(0, 0), (1, 1), (2, 2), (2, 3), (3, 3), (4, 3), (4, 0), (5, 1), (6, 2)]
            ),
            PLF([(0, 0), (2, 2), (2, 3), (4, 3), (4, 0), (6, 2)]),
        ),
        (
            PLF(
                [
                    (0, 2.0),
                    (0, 2.0),
                    (0.25, 2.25),
                    (0.5, 2.0),
                    (1, 1.5),
                    (1, 1.5),
                    (1.75, 1.5),
                    (2, 1),
                    (2, 1),
                ]
            ),
            PLF([(0, 2), (0.25, 2.25), (1, 1.5), (1.75, 1.5), (2, 1)]),
        ),
    ],
)
def test_2(input: PLF, expected: PLF):
    result = input.simplified()
    assert result == expected
