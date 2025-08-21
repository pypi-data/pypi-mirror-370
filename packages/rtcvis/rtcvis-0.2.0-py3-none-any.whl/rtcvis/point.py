class Point:
    def __init__(self, x: float, y: float) -> None:
        """A 2D point with coordinates x and y.

        Objects of this class should not be mutated.

        Args:
            x (float): x coordinate
            y (float): y coordinate
        """
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other) -> bool:
        if type(other) is Point:
            return other.x == self.x and other.y == self.y
        if type(other) is tuple:
            return len(other) == 2 and other[0] == self.x and other[1] == self.y
        return False
