from typing import Optional

from rtcvis.exceptions import ValidationException
from rtcvis.point import Point


class Line:
    def __init__(
        self, a: Point | tuple[float, float], b: Point | tuple[float, float]
    ) -> None:
        """A line defined by two non-identical points.

        This line will be considered to be defined for all x, not just between a.x and
        b.x. An exception is when a.x == b.x: Lines are allowed to be vertical, but
        they'll then only be defined for that single x.

        Note that the properties a and b of instances of this class may be swapped to
        ensure that a.x <= b.x, which makes dealing with Lines easier.

        Args:
            a (Point | tuple[float, float]): The first point, either given as an
                instance of the Point class or as tuple of x and y coordinates.
            b (Point | tuple[float, float]): The second point, either given as an
                instance of the Point class or as tuple of x and y coordinates.
        """

        if a == b:
            raise ValidationException("Points a and b must not be identical.")

        # Turn a and b into Points if they aren't already
        if not isinstance(a, Point):
            a = Point(a[0], a[1])
        if not isinstance(b, Point):
            b = Point(b[0], b[1])

        # Swap a and b if a.x > b.x
        self._a, self._b = (a, b) if (a.x <= b.x) else (b, a)

        if b.x != a.x:
            # normal line
            self._slope: Optional[float] = (b.y - a.y) / (b.x - a.x)
            self._is_vertical = False
        else:
            # vertical line
            self._slope = None
            self._is_vertical = True

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def is_vertical(self):
        return self._is_vertical

    @property
    def slope(self):
        return self._slope

    def point_at_x(self, x: float) -> Optional[Point]:
        """Computes the Point at x.

        Args:
            x (float): x coordinate of the new point

        Returns:
            Optional[Point]: The point on this line at the given x if there is exactly
                one, else None.
        """
        if self.is_vertical:
            return None

        y = self.slope * (x - self.a.x) + self.a.y
        return Point(x, y)


def line_intersection(a: Line, b: Line) -> Optional[Point]:
    """Computes the intersection of two lines.

    Args:
        a (Line): First line.
        b (Line): Second line.

    Returns:
        Optional[Point]: The intersection of lines a and b if there is exactly one,
            else None.
    """
    # Vertical lines cannot have exactly one intersection
    if a.is_vertical and b.is_vertical:
        return None

    a1, _, m_a = a.a, a.b, a.slope
    b1, _, m_b = b.a, b.b, b.slope

    # handle the case of one line being vertical differently
    if a.is_vertical:
        return b.point_at_x(a1.x)
    if b.is_vertical:
        return a.point_at_x(b1.x)

    # both a and b are now non-vertical and thus have a slope
    assert m_a is not None and m_b is not None

    # Parallel lines cannot have exactly one intersection
    if m_a == m_b:
        return None

    # The lines are now guaranteed to have exactly one intersection
    x = (b1.y - a1.y + m_a * a1.x - m_b * b1.x) / (m_a - m_b)
    y = m_a * (x - a1.x) + a1.y

    return Point(x, y)
