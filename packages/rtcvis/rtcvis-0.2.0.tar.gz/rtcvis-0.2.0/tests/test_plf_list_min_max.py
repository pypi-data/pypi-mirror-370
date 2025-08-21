import pytest

from rtcvis import PLF
from rtcvis.plf import plf_list_min_max


@pytest.mark.parametrize(
    "plfs,expected",
    [
        (
            [
                PLF([(0, 0), (1, 2), (2, 2)]),
                PLF([(0, 0.5), (1.5, 0.5), (2, 2.5), (2.5, 2.5)]),
            ],
            PLF(
                [
                    (0, 0),
                    (0.25, 0.5),
                    (1.5, 0.5),
                    (1.875, 2),
                    (2, 2),
                    (2, 2.5),
                    (2.5, 2.5),
                ]
            ),
        )
    ],
)
def test_plf_list_min(plfs: list[PLF], expected: PLF):
    result = plf_list_min_max(plfs, compute_min=True)
    assert result == expected
