import pytest

from rtcvis import PLF
from rtcvis.exceptions import RTCVisException


@pytest.mark.parametrize(
    "plf,x",
    [
        (PLF([]), 0),
        (PLF([(-1, 0)]), 0),
        (PLF([(1, 0)]), 0),
        (PLF([(1, 0), (3, 5)]), 0.9),
    ],
)
def test_plf_get_value_invalid(plf: PLF, x: float):
    with pytest.raises(RTCVisException):
        plf.get_value(x)


def test_plf_get_value():
    assert PLF([(5, 3)]).get_value(5) == 3
    a = PLF([(-1, 0), (0, 1), (1, -1)])
    assert a.get_value(-1) == 0
    assert a.get_value(-0.5) == 0.5
    assert a.get_value(-0.1) == 0.9
    assert a.get_value(0) == 1
    assert a.get_value(0.5) == 0
    assert a.get_value(0.75) == -0.5
    assert a.get_value(1) == -1
