from enum import Enum
from typing import Optional

from rtcvis.plf import PLF, plf_list_min_max
from rtcvis.point import Point

LAMBDA = r"\lambda"
DELTA = r"\Delta"


class ConvType(Enum):
    """All types of (de-)convolutions."""

    MAX_PLUS_CONV = 0
    MAX_PLUS_DECONV = 1
    MIN_PLUS_CONV = 2
    MIN_PLUS_DECONV = 3

    def __str__(self) -> str:
        """Returns the name of the convolution.

        Returns:
            str: The name of the convolution.
        """
        match self:
            case ConvType.MAX_PLUS_CONV:
                return "Max-Plus-Convolution"
            case ConvType.MAX_PLUS_DECONV:
                return "Max-Plus-Deconvolution"
            case ConvType.MIN_PLUS_CONV:
                return "Min-Plus-Convolution"
            case ConvType.MIN_PLUS_DECONV:
                return "Min-Plus-Deconvolution"

    @property
    def is_deconv(self) -> bool:
        return self in (ConvType.MAX_PLUS_DECONV, ConvType.MIN_PLUS_DECONV)

    @property
    def a_desc(self) -> str:
        return rf"$a({LAMBDA})$"

    @property
    def b_desc(self) -> str:
        return rf"$b({LAMBDA})$"

    @property
    def a_trans_desc(self) -> str:
        return rf"$a({DELTA} {'+' if self.is_deconv else '-'} {LAMBDA})$"

    @property
    def sum_desc(self) -> str:
        return (
            f"${self.a_trans_desc[1:-1]}"
            + ("-" if self.is_deconv else "+")
            + f"{self.b_desc[1:-1]}$"
        )

    @property
    def operator_desc(self) -> str:
        match self:
            case ConvType.MAX_PLUS_CONV:
                op = r"\overline{\otimes}"
            case ConvType.MAX_PLUS_DECONV:
                op = r"\overline{\oslash}"
            case ConvType.MIN_PLUS_CONV:
                op = r"\otimes"
            case ConvType.MIN_PLUS_DECONV:
                op = r"\oslash"
        return rf"$(a {op} b)({DELTA})$"

    @property
    def full_desc(self) -> str:
        match self:
            case ConvType.MAX_PLUS_CONV:
                op = r"\text{sup}_{0 \leq \lambda \leq \Delta}"
            case ConvType.MAX_PLUS_DECONV:
                op = r"\text{inf}_{\lambda \geq 0}"
            case ConvType.MIN_PLUS_CONV:
                op = r"\text{inf}_{0 \leq \lambda \leq \Delta}"
            case ConvType.MIN_PLUS_DECONV:
                op = r"\text{sup}_{\lambda \geq 0}"

        return f"${op}" + r"\{" + self.sum_desc[1:-1] + r"\}$"


class ConvAtXResult:
    def __init__(self, transformed_a: PLF, sum: PLF, result: Point) -> None:
        """The result of a convolution at a specific x.

        Args:
            transformed_a (PLF): The shifted and optionally mirrored PLF a.
            sum (PLF): The sum or difference between the transformed PLF a and PLF b.
            result (Point): The point which has the minimum/maximum value of the sum
                PLF, depending on the type of convolution. Its y value is the actual
                result of the convolution.
        """
        self._transformed_a = transformed_a
        self._sum = sum
        self._result = result

    @property
    def transformed_a(self) -> PLF:
        return self._transformed_a

    @property
    def sum(self) -> PLF:
        return self._sum

    @property
    def result(self) -> Point:
        return self._result


def conv_at_x(a: PLF, b: PLF, delta_x: float, conv_type: ConvType) -> ConvAtXResult:
    """Computes the given type of convolution of a and b at the given x.

    Args:
        a (PLF): PLF a
        b (PLF): PLF b
        delta_x (float): The x at which to evaluate the convolution.
        conv_type (ConvType): The type of convolution

    Returns:
        ConvAtXResult: An object containing several properties of the result.
    """
    if conv_type == ConvType.MIN_PLUS_CONV or conv_type == ConvType.MAX_PLUS_CONV:
        transformed_a = a.transformed(mirror=True, offset=delta_x)
        s = transformed_a + b
    else:
        transformed_a = a.transformed(mirror=False, offset=-delta_x)
        s = transformed_a - b
    if conv_type == ConvType.MIN_PLUS_CONV or conv_type == ConvType.MAX_PLUS_DECONV:
        result = s.min
    else:
        result = s.max
    return ConvAtXResult(transformed_a=transformed_a, sum=s, result=result)


def conv(
    a: PLF,
    b: PLF,
    conv_type: ConvType,
    start: Optional[float] = None,
    stop: Optional[float] = None,
) -> PLF:
    """Computes the convolution of two PLFs.

    Args:
        a (PLF): The first PLF.
        b (PLF): The second PLF.
        conv_type (ConvType): The type of convolution.
        start (Optional[float], optional): Where the resulting PLF's start should be
            truncated. Can be set to None if the result shouldn't be truncated.
            Defaults to None.
        stop (Optional[float], optional): Where the resulting PLF's end should be
            truncated. Can be set to None if the result shouldn't be trunated.
            Defaults to None.

    Returns:
        PLF: The result of the convolution.
    """
    # create len(a.points) functions by adding b's points to a
    wsogmm1: list[PLF] = []
    is_deconv = conv_type in (ConvType.MIN_PLUS_DECONV, ConvType.MAX_PLUS_DECONV)
    # convolutions mirror a first, which is why we need to add the x coordinates
    # deconvolutions dont mirror, which is why we need to subtract the x coordinates
    subtract_x = is_deconv
    # convolutions add the y values, deconvolutions subtract them
    subtract_y = is_deconv
    for p in b.points:
        wsogmm1.append(
            a.add_point(other=p, subtract_x=subtract_x, subtract_y=subtract_y)
        )

    # reverse the list if we're doing a deconvolution because they're currently given
    # in descending of x-coordinates
    if is_deconv:
        wsogmm1 = list(reversed(wsogmm1))

    wsogmm2: list[PLF] = []
    # now we create new PLFs by connecting the i-th point of each function in the
    # correct order and we do this for all points those functions
    for i in range(len(a.points)):
        wsogmm2.append(PLF([wsogmm1[j].points[i] for j in range(len(b.points))]))

    # Now we just need to compute the minimum or maximum over all those PLFs :)
    compute_min = conv_type in (ConvType.MIN_PLUS_CONV, ConvType.MAX_PLUS_DECONV)
    plf_list = (
        (wsogmm1 + wsogmm2)
        if (a.x_end - a.x_start) > (b.x_end - b.x_start)
        else (wsogmm2 + wsogmm1)
    )
    result: PLF = plf_list_min_max(plf_list, compute_min=compute_min)

    # Optionally truncate the start/end
    if start is not None:
        result = result.start_truncated(start)
    if stop is not None:
        result = result.end_truncated(stop)

    # remove redundant points
    result = result.simplified()

    return result
