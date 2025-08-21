import pytest

from rtcvis import PLF, ConvType, conv, conv_at_x

min_conv_test_cases = [
    (
        PLF([(0, 2), (5, 4.5)]),
        PLF([(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]),
        PLF([(0, 2), (1, 2), (10, 6.5)]),
    ),
    (
        PLF([(0, 0), (2.5, 1), (5, 6)]),
        PLF([(0, 0), (4, 2), (5, 3)]),
        PLF([(0, 0), (2.5, 1), (6.5, 3), (7.5, 4), (10, 9)]),
    ),
    (
        PLF([(0, 1.5), (0, 2), (1, 1), (2, 1)]),
        PLF([(0, 0.5), (0.5, 1), (1, 0), (2, 0)]),
        PLF([(0, 2), (0.25, 2.25), (1, 1.5), (1.5, 1.5), (2, 1), (4, 1)]),
    ),
]


max_conv_test_cases = [
    (
        PLF([(0, 2), (5, 4.5)]),
        PLF([(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]),
        PLF([(0, 2), (9, 6.5), (10, 6.5)]),
    ),
    (
        PLF([(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (5, 3)]),
        PLF([(0, 0), (1, 0), (8, 7)]),
        PLF(
            [
                (0, 0),
                (1, 0),
                (1, 1),
                (2, 1),
                (2, 2),
                (3, 2),
                (3, 3),
                (4, 3),
                (11, 10),
                (13, 10),
            ]
        ),
    ),
]


min_deconv_test_cases = [
    (
        PLF([(0, 2), (5, 3.25)]),
        PLF([(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]),
        PLF([(0, 2.25), (4, 3.25), (5, 3.25)]),
    ),
    (
        PLF([(0, 0), (9, 9), (15, 9)]),
        PLF([(0, 0), (2, 0), (15, 13)]),
        PLF([(0, 2), (7, 9), (15, 9)]),
    ),
]


max_deconv_test_cases = [
    (
        PLF(
            [
                (0, 0),
                (8, 8),
                (8, 7),
                (11, 10),
                (11, 8),
                (12, 9),
                (12, 8),
                (13, 9),
                (13, 7),
                (15, 7),
                (15, 4),
            ]
        ),
        PLF([(0, 0), (15, 0)]),
        PLF([(0, 0), (4, 4), (15, 4)]),
    ),
]


@pytest.mark.parametrize("a,b,expected", min_conv_test_cases)
def test_min_plus_conv(a: PLF, b: PLF, expected: PLF):
    result = conv(a=a, b=b, conv_type=ConvType.MIN_PLUS_CONV)
    assert result == expected


@pytest.mark.parametrize("a,b,expected", max_conv_test_cases)
def test_max_plus_conv(a: PLF, b: PLF, expected: PLF):
    result = conv(a=a, b=b, conv_type=ConvType.MAX_PLUS_CONV)
    assert result == expected


@pytest.mark.parametrize("a,b,expected", min_deconv_test_cases)
def test_min_plus_deconv(a: PLF, b: PLF, expected: PLF):
    result = conv(a=a, b=b, conv_type=ConvType.MIN_PLUS_DECONV, start=0)
    assert result == expected


@pytest.mark.parametrize("a,b,expected", max_deconv_test_cases)
def test_max_plus_deconv(a: PLF, b: PLF, expected: PLF):
    result = conv(a=a, b=b, conv_type=ConvType.MAX_PLUS_DECONV, start=0)
    assert result == expected


def conv_at_x_helper(a: PLF, b: PLF, expected: PLF, conv_type: ConvType):
    """Helper for testing the conv_at_x function.

    Samples some points of the expected result and checks whether the result of calling
    conv_at_x is the same.

    Args:
        a (PLF): First PLF.
        b (PLF): Second PLF.
        expected (PLF): Expected result.
        conv_type (ConvType): The type of convolution.
    """
    POINTS_PER_INTERVAL = 3
    compute_min = conv_type in (ConvType.MIN_PLUS_CONV, ConvType.MAX_PLUS_DECONV)
    op = min if compute_min else max
    for p1, p2 in zip(expected.points[:], expected.points[1:]):
        if p1.x == p2.x:
            # two points at the same x -> check the y coordinate of the correct one
            y_result = conv_at_x(a=a, b=b, delta_x=p1.x, conv_type=conv_type).result.y
            y_expected = op(p1.y, p2.y)
            assert y_result == y_expected
        else:
            # points at different x -> check some points between them
            interval_len = p2.x - p1.x
            step_size = interval_len / (POINTS_PER_INTERVAL + 1)
            steps = [p1.x + (i + 1) * step_size for i in range(POINTS_PER_INTERVAL)]
            for x in steps:
                y_result = conv_at_x(a=a, b=b, delta_x=x, conv_type=conv_type).result.y
                y_expected = expected.get_value(x)
                assert y_result == y_expected


@pytest.mark.parametrize("a,b,expected", min_conv_test_cases)
def test_min_plus_conv_at_x(a: PLF, b: PLF, expected: PLF):
    conv_at_x_helper(a=a, b=b, expected=expected, conv_type=ConvType.MIN_PLUS_CONV)


@pytest.mark.parametrize("a,b,expected", max_conv_test_cases)
def test_max_plus_conv_at_x(a: PLF, b: PLF, expected: PLF):
    conv_at_x_helper(a=a, b=b, expected=expected, conv_type=ConvType.MAX_PLUS_CONV)


@pytest.mark.parametrize("a,b,expected", min_deconv_test_cases)
def test_min_plus_deconv_at_x(a: PLF, b: PLF, expected: PLF):
    conv_at_x_helper(a=a, b=b, expected=expected, conv_type=ConvType.MIN_PLUS_DECONV)


@pytest.mark.parametrize("a,b,expected", max_deconv_test_cases)
def test_max_plus_deconv_at_x(a: PLF, b: PLF, expected: PLF):
    conv_at_x_helper(a=a, b=b, expected=expected, conv_type=ConvType.MAX_PLUS_DECONV)
