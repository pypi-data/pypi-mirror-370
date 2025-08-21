import pytest

from rtcvis import PLF
from rtcvis.exceptions import ValidationException


@pytest.mark.parametrize(
    "plf_points",
    [
        # just check that these don't raise any exceptions
        [],
        [(0, 0)],
        [(0.1, 0), (1, 1)],
        [(-0.1, 0), (1, 1)],
        [(-1, 0), (0.5, 1), (0.5, 2), (2, 0)],
        [(-1, 0), (0.5, 1), (0.5, 1), (2, 0)],
        [(1, 1), (1, 2)],
        [(1, 1), (1, 1)],
    ],
)
def test_plf_init(plf_points):
    PLF(plf_points)


@pytest.mark.parametrize(
    "plf_points",
    [
        [(1, 0), (0, 0)],
        [(-1, 0), (0.5, 1), (0.5, 2), (0.5, 3), (2, 0)],
    ],
)
def test_plf_init_invalid(plf_points):
    with pytest.raises(ValidationException):
        PLF(plf_points)
