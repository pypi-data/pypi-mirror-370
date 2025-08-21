import operator
from typing import Sequence, Union

from rtcvis.exceptions import RTCVisException, ValidationException
from rtcvis.line import Line, line_intersection
from rtcvis.point import Point


class PLF:
    def __init__(self, points: Sequence[Point | tuple[float, float]]) -> None:
        """A piecewise linear function defined by a list of points.

        The function must be defined at everywhere between the first and the last point.
        It is allowed to have discontinuities by specifying two points at the same x
        coordinate. The function may also have only 1 or 0 points.

        Args:
            points (Sequence[Point | tuple[float, float]]): The points which define the
                PLF. They must be in the correct order (x may not decrease). The list
                elements can either be Point instances or tuples of x and y coordinates.
        """
        self._points = _points = [
            p if isinstance(p, Point) else Point(*p) for p in points
        ]
        self._x = _x = [p.x for p in _points]
        self._y = _y = [p.y for p in _points]

        if len(_points) > 1 and not all(
            _x[i] <= _x[i + 1] for i in range(len(_points) - 1)
        ):
            raise ValidationException("The points must have ascending x coordinates.")
        if len(_points) > 2 and not all(
            (_x[i] != _x[i + 1]) or (_x[i + 1] != _x[i + 2])
            for i in range(len(_points) - 2)
        ):
            raise ValidationException(
                "There may not be more than two points with the same x coordinate."
            )

        if len(_points) == 0:
            self._x_start = 0.0
            self._x_end = 0.0
            self._min = Point(0, 0)
            self._max = Point(0, 0)
        else:
            self._x_start = _x[0]
            self._x_end = _x[-1]
            self._min = Point(_x[_y.index(min(_y))], min(_y))
            self._max = Point(_x[_y.index(max(_y))], max(_y))

    @property
    def x_start(self):
        return self._x_start

    @property
    def x_end(self):
        return self._x_end

    @property
    def points(self):
        return self._points

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __repr__(self) -> str:
        return f"PLF([{', '.join([repr(point) for point in self.points])}])"

    def __eq__(self, other) -> bool:
        if type(other) is not PLF or len(self.points) != len(other.points):
            return False

        return all(a == b for a, b in zip(self.points, other.points))

    @classmethod
    def from_rtctoolbox(
        cls, points: list[tuple[float, float, float]], x_end: float
    ) -> "PLF":
        """Constructs a PLF from rtctoolbox-like arguments.

        Note that rtcvis can only handle finite and aperiodic functions.

        Args:
            points (list[tuple[float, float, float]]): List of (x, y, slope) tuples.
                Must be given in order of strictly ascending x coordinates. Only the
                first two points may be defined at the same x to allow for
                discontinuities at the start.
            x_end (float): The x coordinate where the function should end.

        Returns:
            PLF: The corresponding PLF.
        """
        # The first point may be defined at the same (or a greater) x as the second
        # point to allow for discontinuities right at the start
        if len(points) > 1 and not (points[0][0] <= points[1][0]):
            raise ValidationException(
                "The x value of the second point must be greater"
                + " or equal to the x value of the first point."
            )

        # All further points must be defined at increasing x coordinates
        for p1, p2 in zip(points[1:], points[2:]):
            if not (p1[0] < p2[0]):
                raise ValidationException(
                    "All points except for the second one must have greater x values"
                    + " than their predecessor."
                )

        _points = []
        for i, (x, y, slope) in enumerate(points):
            # stop if this point lies behind x_end
            if x > x_end:
                break

            # Always add this point
            _points.append(Point(x, y))

            # Check if this point is the start of a new segment and find the end of
            # that segment
            if i == (len(points) - 1):
                # This was the last point
                if x == x_end:
                    # The last point was defined at x_end
                    break
                # The end of the current segment is x_end
                segment_end_x = x_end
            else:
                # The end of the current segment is the x coordinate of the next point
                segment_end_x = points[i + 1][0]
                if x == segment_end_x:
                    # the next point is defined at the same x coordinate, so no segment
                    # is started here
                    continue

            is_last_iteration = False
            if segment_end_x > x_end:
                is_last_iteration = True
                segment_end_x = x_end

            # Compute the y coordinate of the segment end
            segment_len = segment_end_x - x
            segment_end_y = y + slope * segment_len

            if (
                i != (len(points) - 1)
                and segment_end_x == points[i + 1][0]
                and segment_end_y == points[i + 1][1]
            ):
                # The next point starts exactly where this line ends and will be added
                # in the next iteration anyway
                continue

            next_point = Point(x=segment_end_x, y=segment_end_y)
            _points.append(next_point)

            if is_last_iteration:
                break

        return PLF(_points)

    def start_truncated(self, x_start: float) -> "PLF":
        """Creates a new PLF that is truncated at the start.

        The new PLF has the same function values at all x >= x_start, but it is not
        defined for any x < x_start.

        Args:
            x_start (float): The x coordinate at which to truncate the PLF.

        Returns:
            PLF: The truncated PLF.
        """
        if self.x_start >= x_start:
            return self

        for idx, point in enumerate(self.points):
            if point.x >= x_start:
                # This is the first point located after x_start
                points = []
                if point.x > x_start:
                    # create a new point at x_start if there isn't one already
                    new_point = Line(self.points[idx - 1], self.points[idx]).point_at_x(
                        x_start
                    )
                    assert new_point is not None
                    points = [new_point]
                # append all remaining points
                points += self.points[idx:]
                return PLF(points)
        return PLF([])

    def end_truncated(self, x_end: float) -> "PLF":
        """Creates a new PLF that is truncated at the end.

        The new PLF has the same function values at all x <= x_end, but it is not
        defined for any x > x_end.

        Args:
            x_end (float): The x coordinate at which to truncate the PLF.

        Returns:
            PLF: The truncated PLF.
        """
        if self.x_end <= x_end:
            return self

        for idx, point in reversed(list(enumerate(self.points))):
            if point.x <= x_end:
                # This is the first point located before x_start
                points = []
                if point.x < x_end:
                    # create a new point at x_end if there isn't one already
                    new_point = Line(self.points[idx + 1], self.points[idx]).point_at_x(
                        x_end
                    )
                    assert new_point is not None
                    points = [new_point]
                # prepend all remaining points
                points = list(self.points[: idx + 1]) + points
                return PLF(points)
        return PLF([])

    def __add__(self, other: Union["PLF", Point]) -> "PLF":
        if isinstance(other, PLF):
            return self.add_plf(other, False)
        else:
            return self.add_point(other, False, False)

    def add_plf(self, other: "PLF", subtract_y: bool) -> "PLF":
        """Adds the other function to self.

        The result will be returned and self will not be modified.

        Args:
            other (PLF): The other function to add to self.
            subtract_y (bool): Whether to instead subtract the y values of other from
                self.

        Returns:
            PLF: The sum of the two functions.
        """
        a, b = match_plf(self, other)
        op = operator.sub if subtract_y else operator.add
        new_points = [Point(p1.x, op(p1.y, p2.y)) for p1, p2 in zip(a.points, b.points)]
        return PLF(new_points).simplified()

    def __sub__(self, other: Union["PLF", Point]) -> "PLF":
        if isinstance(other, PLF):
            return self.add_plf(other, subtract_y=True)
        else:
            return self.add_point(other, True, True)

    def transformed(self, mirror: bool, offset: float) -> "PLF":
        """Used for creating shifted and mirrored PLFs.

        The new PLF is offset on the x-Axis and optionally mirrored on the y-Axis.
        Note that the function will first be mirrored and then offset, meaning that
        positive offset values will shift the function to the right.

        Args:
            mirror (bool): Whether the function should first be mirrored on the y-Axis.
            offset (float): Amount which will be added to each point's x-coordinate.

        Returns:
            PLF: The transformed function.
        """
        new_points: list[Point] = []
        factor = -1 if mirror else 1
        # iterate over the points in the order in which they'll be
        # in the transformed PLF
        points = iter(self.points) if mirror else reversed(self.points)
        for point in points:
            new_x = factor * point.x + offset
            new_points.insert(0, Point(new_x, point.y))

        return PLF(new_points)

    def get_value(self, x: float) -> float:
        """Computes and returns the value of this PLF at the given x.

        Note that if there are two points defined at the same x, the value of the first
        one will be returned.

        Args:
            x (float): x coordinate

        Returns:
            float: The result
        """
        if len(self.points) == 0:
            raise RTCVisException(
                "The PLF is undefined everywhere and thus does not have a value"
                + " anywhere."
            )
        if not (x >= self.x_start and x <= self.x_end):
            raise RTCVisException(
                f"The PLF is only defined between {self.x_start} and {self.x_end} and"
                + f" thus does not have a value at {x}."
            )

        for idx, p in enumerate(self.points):
            if p.x == x:
                return p.y
            elif p.x > x:
                p_at_x = Line(self.points[idx - 1], self.points[idx]).point_at_x(x)
                assert p_at_x is not None
                return p_at_x.y
        assert False, "Did not find points with corresponding x coordinates"

    def __call__(self, x: float) -> float:
        """Calls self.get_value(x)."""
        return self.get_value(x)

    def simplified(self) -> "PLF":
        """Returns an equal PLF with redundant points removed.

        This function returns a copy of this PLF where there are no three subsequent
        points that are all located on the same line or at the exact same coordinates.
        self will not be modified.

        Returns:
            PLF: The simplified PLF.
        """
        if len(self.points) <= 1:
            # if we have at most 1 points, there are no redundant points
            return self

        # go over self.points and remove all duplicate points
        dedup = [self.points[0]]
        for i in range(len(self.points) - 1):
            if self.points[i] != self.points[i + 1]:
                dedup.append(self.points[i + 1])

        if len(dedup) < 3:
            # if there's at most 2 points left, they cannot be redundant
            return PLF(dedup)

        # already insert the first point
        new_points = [dedup[0]]

        # now append all the intermediate points that are not redundant
        for i in range(len(dedup) - 2):
            a, b, c = dedup[i], dedup[i + 1], dedup[i + 2]
            if Line(a, b).slope != Line(b, c).slope:
                new_points.append(b)

        # finally append the last point
        new_points.append(dedup[-1])

        return PLF(new_points)

    def add_point(self, other: Point, subtract_x: bool, subtract_y: bool) -> "PLF":
        """Adds the given point to all points of self.

        The coordinates of the other point will be added to the coordinates of all
        Points of this PLF. Returns a new PLF instead of modifying self.

        Args:
            other (Point): The Point to add to this PLF.
            subtract_x (bool): Whether to instead subtract other.x from the points.
            subtract_y (bool): Whether to instead subtract other.y from the points.

        Returns:
            PLF: The resulting PLF.
        """
        x_op = operator.sub if subtract_x else operator.add
        y_op = operator.sub if subtract_y else operator.add
        return PLF([Point(x_op(p.x, other.x), y_op(p.y, other.y)) for p in self.points])


def match_plf(a: "PLF", b: "PLF") -> tuple["PLF", "PLF"]:
    """Matches two PLFs and returns the result.

    After matching the PLFs, they will have the same number of points and the points of
    those two functions will always be defined at the same x coordinates. The given
    PLFs will not be modified.

    Returns:
        tuple["PLF", "PLF"]: The matched functions.
    """
    # Truncate the functions so they start/end at the same x coordinates
    a = a.start_truncated(b.x_start).end_truncated(b.x_end)
    b = b.start_truncated(a.x_start).end_truncated(a.x_end)

    if len(a.points) == 0 or len(b.points) == 0:
        # the functions are not overlapping -> return empty PLFs
        return PLF([]), PLF([])

    # iterate over the points of a and b, add their points and insert a new point for a
    # or b if it does not have a point at an x where the other PLF does have a point
    # When inserting a new point, we need to know the previous point so that we can
    # compute a new point on the line from the previous to the next point
    # Note that constructing the Line objects here is fine, the two points can never be
    # at the same x (I think)
    new_a, new_b = [], []
    a_idx, b_idx = 0, 0
    while a_idx < len(a.points) and b_idx < len(b.points):
        a_x = a.points[a_idx].x
        b_x = b.points[b_idx].x

        if a_x == b_x:
            # The points are already at the same x coordinate
            new_a.append(a.points[a_idx])
            new_b.append(b.points[b_idx])
            a_idx += 1
            b_idx += 1
        elif a_x < b_x:
            # Insert a new point for b
            new_a.append(a.points[a_idx])
            new_b.append(
                Line(b.points[b_idx - 1], b.points[b_idx]).point_at_x(a.points[a_idx].x)
            )
            a_idx += 1
        else:
            # Insert a new point for a
            new_a.append(
                Line(a.points[a_idx], a.points[a_idx - 1]).point_at_x(b.points[b_idx].x)
            )
            new_b.append(b.points[b_idx])
            b_idx += 1

    # If we've reached the end of one PLF, the other one might still have another
    # point at the same x coordinate which we need to append, which also means that
    # we must duplicate the last point of the other PLF
    if a_idx != len(a.points):
        assert a_idx == len(a.points) - 1
        new_a.append(a.points[a_idx])
        new_b.append(new_b[-1])
    if b_idx != len(b.points):
        assert b_idx == len(b.points) - 1
        new_b.append(b.points[b_idx])
        new_a.append(new_a[-1])

    return PLF(new_a), PLF(new_b)


def plf_min_max(a: PLF, b: PLF, compute_min: bool) -> PLF:
    """Computes the minimum or maximum of two PLFs.

    The returned PLF will have the value of min(a(x), b(x)) if compute_min=True or
    max(a(x), b(x)) if compute_min=False for all x for which a and b are both defined.
    It will be undefined at all other points.

    Args:
        a (PLF): First PLF.
        b (PLF): Second PLF.
        compute_min (bool): If True, the resulting function will be the minimum of a
            and b, else it will be the maximum.

    Returns:
        PLF: The minimum/maximum of a and b.
    """
    a, b = match_plf(a, b)

    if len(a.points) == 0:
        # return if a and b were not overlapping
        return a

    # get the <= or >= operator
    compare = operator.le if compute_min else operator.ge

    new_points = []

    for i in range(len(a.points) - 1):
        # append the point with the smaller/greater y
        if compare(a.y[i], b.y[i]):
            new_points.append(a.points[i])
        else:
            new_points.append(b.points[i])

        # check for an intersection in the next line segment
        # Skip this step if a or b have two points at the same x, creating Lines and
        # checking for intersections wouldn't make sense or even work
        if a.points[i].x != a.points[i + 1].x and b.points[i].x != b.points[i + 1].x:
            intersection = line_intersection(
                Line(a.points[i], a.points[i + 1]), Line(b.points[i], b.points[i + 1])
            )
            if intersection and intersection.x > a.x[i] and intersection.x < a.x[i + 1]:
                # there's an intersection and it's not at the start/end of the segment
                new_points.append(intersection)

    # also add the last point
    new_points.append(a.points[-1] if compare(a.y[-1], b.y[-1]) else b.points[-1])

    result = PLF(new_points)

    # The PLF might still have redundant points, remove them
    return result.simplified()


def plf_merge(a: PLF, b: PLF) -> PLF:
    """Returns a PLF that has the value of a everywhere it's and else the value of b.

    Note that a and b must be overlapping or at least touching.

    Args:
        a (PLF): The dominant PLF.
        b (PLF): The other PLF.

    Returns:
        PLF: The result of merging a and b.
    """
    # If one of the PLFs is empty, return the other
    if not len(a.points):
        return b
    if not len(b.points):
        return a

    # The PLFs are not empty -> check that they're overlapping
    if not (b.x_start <= a.x_end and b.x_end >= a.x_start):
        raise RTCVisException("The provided PLFs must overlap.")

    # The general idea is to just take b from its start to a.x_start
    # and from a.x_end to its end. But we might have to remove some
    # points at the starts/ends because there may only be two points
    # at the same x

    # get b from its start until a.x_start
    if b.x_start < a.x_start:
        b_end_truncated = b.end_truncated(a.x_start)
        start_points = list(b_end_truncated.points)
        # remove the last point if there's another point at that x
        if len(start_points) >= 2 and b_end_truncated.x[-2] == b_end_truncated.x[-1]:
            start_points.pop(-1)
    else:
        start_points = []

    # get b from a.x_end until b's end
    if b.x_end > a.x_end:
        b_start_truncated = b.start_truncated(a.x_end)
        end_points = list(b_start_truncated.points)
        # remove the first point if there's another point at that x
        if len(end_points) >= 2 and b_start_truncated.x[0] == b_start_truncated.x[1]:
            end_points.pop(0)
    else:
        end_points = []

    # the middle part is the part that's defined by a
    middle_points = list(a.points)
    # remove the first point if there's another point at that x and there start_points
    if start_points and len(middle_points) >= 2 and a.x[0] == a.x[1]:
        middle_points.pop(0)
    # remove the last point if there's another point at that x and there are end_points
    if end_points and len(middle_points) >= 2 and a.x[-2] == a.x[-1]:
        middle_points.pop(-1)

    # now just concatenate all point lists
    return PLF(start_points + middle_points + end_points)


def plf_list_min_max(plfs: Sequence[PLF], compute_min: bool) -> PLF:
    result = plfs[0]
    for plf in plfs[1:]:
        new_min_max = plf_min_max(a=result, b=plf, compute_min=compute_min)
        merged = plf_merge(
            plf_merge(new_min_max, result),
            plf,
        )
        result = merged
    return result
