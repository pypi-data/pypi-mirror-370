from typing import Self, Optional, Iterator
import numpy as np
from numpy.typing import NDArray


class Coords:
    _coords: NDArray[np.float32]
    __slots__ = ("_coords",)

    def __init__(self, arr: NDArray[np.float32]) -> None:
        """init"""
        self._coords = np.asarray(arr, dtype=np.float32)  # Явное приведение типа
        self._coords.flags.writeable = False

    def __mul__(self, other: int | float) -> Self:
        return self.__class__(arr=self._coords * other)

    def __truediv__(self, other: int | float) -> Self:
        return self.__class__(arr=self._coords / other)

    def __floordiv__(self, other: int | float) -> Self:
        return self.__class__(arr=self._coords / other)

    def __iter__(self) -> Iterator[float]:
        # yield from self._coords.flat
        yield from (float(x) for x in self._coords.flat)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Coords):
            return bool(np.equal(self._coords, other._coords).all())
        raise NotImplementedError


class Point(Coords):
    def __init__(self, *coords: int | float, arr: Optional[NDArray[np.float32]] = None, x: Optional[int | float] = None, y: Optional[int | float] = None) -> None:
        if arr is not None:
            super().__init__(arr)
        else:
            if x is not None or y is not None:
                coords = (
                    x if isinstance(x, (int, float)) else 0,
                    y if isinstance(y, (int, float)) else 0
                )
            elif len(coords) == 0:
                coords = (0, 0)
            elif len(coords) != 2:
                raise ValueError(F"{self.__class__.__name__} got not one pair values")
            super().__init__(np.array(coords, dtype=np.float32).reshape(1, 2))

    @property
    def x(self) -> float:
        return float(self._coords[0, 0])

    @x.setter
    def x(self, value: float) -> None:
        self._coords[0, 0] = value

    @property
    def y(self) -> float:
        return float(self._coords[0, 1])

    @y.setter
    def y(self, value: float) -> None:
        self._coords[0, 1] = value

    def __add__(self, other: Self) -> Self:
        return self.__class__(arr=self._coords + other._coords)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(arr=self._coords - other._coords)

    def __mul__(self, other: int | float | Self) -> Self:
        if isinstance(other, Point):
            return self.__class__(arr=self._coords * other._coords)
        else:
            return super().__mul__(other)

    def __truediv__(self, other: int | float | Self) -> Self:
        if isinstance(other, Point):
            return self.__class__(arr=self._coords / other._coords)
        else:
            return super().__truediv__(other)

    def __floordiv__(self, other: int | float | Self) -> Self:
        if isinstance(other, Point):
            return self.__class__(arr=self._coords // other._coords)
        else:
            return super().__floordiv__(other)

    def __str__(self) -> str:
        return F"{int(self.x):+}{int(self.y):+}"

    def __getitem__(self, item: int) -> float:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise StopIteration

    def __copy__(self) -> Self:
        return self.__class__(arr=self._coords.copy())

    def unsafely(self) -> Self:
        new = self.__class__(arr=self._coords.copy())
        new._coords.flags.writeable = True
        return new


class Size(Point):
    def __str__(self) -> str:
        return F"{int(self.x)}x{int(self.y)}"

    def x_normalize(self, width: int | float = 1) -> Self:
        """normalize Size to x=1 with keeping proportion"""
        return self / self.x * width

    def with_dimensions(self, x: int | float | None = None, y: int | float | None = None) -> "Size":
        """Returns a new Size instance with modified dimensions.
        Args:
            x: New width value (None keeps current)
            y: New height value (None keeps current)
        Returns:
            New Size instance with updated dimensions
        """
        new_arr = self._coords.copy()
        if x is not None:
            new_arr[0][0] = x
        if y is not None:
            new_arr[0][1] = y
        return self.__class__(arr=new_arr)

    def scaled(self, fx: float, fy: Optional[float] = None) -> "Size":
        """Scale dimensions by given factor(s).
        Args:
            fx: Scale factor for width (or uniform scale if fy is None)
            fy: Optional scale factor for height (defaults to fx if None)
        Returns:
            New Size object with scaled dimensions
        Example:
            >>> Size(100,50).scaled(0.5) → Size(50,25)
            >>> Size(100,50).scaled(2, 1.5) → Size(200,75)
        """
        if fy is None:
            fy = fx
        return self.__class__(arr=self._coords * np.array((fx, fy), dtype=np.float32))


class Polygon(Coords):
    def __init__(self, *coords: int | float, arr: Optional[NDArray[np.float32]] = None) -> None:
        if arr is not None:
            super().__init__(arr)
        elif len(coords) < 2:
            raise ValueError(F"{self.__class__.__name__} got not pair values")
        else:
            super().__init__(np.array(coords, dtype=np.float32).reshape(len(coords) // 2, 2))

    def __add__(self, other: Point) -> Self:
        return self.__class__(arr=self._coords + other._coords)

    def __sub__(self, other: Point) -> Self:
        return self.__class__(arr=self._coords - other._coords)

    def __mul__(self, other: int | float | Point) -> Self:
        if isinstance(other, Point):
            return self.__class__(arr=self._coords * other._coords)
        else:
            return super().__mul__(other)

    def __truediv__(self, other: int | float | Point) -> Self:
        if isinstance(other, Point):
            return self.__class__(arr=self._coords / other._coords)
        else:
            return super().__truediv__(other)

    def __floordiv__(self, other: int | float | Point) -> Self:
        if isinstance(other, Point):
            return self.__class__(arr=self._coords // other._coords)
        else:
            return super().__floordiv__(other)

    @property
    def size(self) -> Size:
        """area occupied by polygon"""
        return Size(arr=(self._coords.max(axis=0) - self._coords.min(axis=0)).reshape(1, 2))

    @property
    def base(self) -> Point:
        """upper left point"""
        return Point(arr=self._coords.min(axis=0).reshape(1, 2))

    def move_to(self, p: Point) -> Self:
        """move base to Point<x, y>"""
        return self + (p - self.base)

    def reshape(self, shape: Size) -> Self:
        return self * (shape / self.size)

    def flip(self, axis: int = 0) -> Self:
        return self.__class__(arr=np.flip(np.flip(self._coords, axis), axis))


class SmoothBox(Polygon):
    @classmethod
    def from_size(cls, size: Size, base: Point = Point(0, 0), prop: float = 0.3, maximal: int = 100) -> Self:
        """Returns 12 points (4 vertices + 8 intermediate)"""
        radius = min(min(*size) * prop, maximal)
        x, y, w, h = base.x, base.y, size.x, size.y
        vertices = np.empty((12, 2), dtype=np.float32)
        vertices[0] = (x, y)
        vertices[1] = (x, y + radius)
        vertices[2] = (x, y + h - radius)
        vertices[3] = (x, y + h)
        vertices[4] = (x + radius, y + h)
        vertices[5] = (x + w - radius, y + h)
        vertices[6] = (x + w, y + h)
        vertices[7] = (x + w, y + h - radius)
        vertices[8] = (x + w, y + radius)
        vertices[9] = (x + w, y)
        vertices[10] = (x + w - radius, y)
        vertices[11] = (x + radius, y)
        return cls(arr=vertices)

    def __str__(self) -> str:
        return F"{self.size}{self.base}"

    @property
    def size(self) -> Size:
        return Size(arr=self.SE._coords - self.NW._coords)

    @property
    def base(self) -> Point:
        return Point(arr=self._coords[0].reshape(1, 2))

    @property
    def NW(self) -> Point:
        """return: North-West widget Point"""
        return self.base

    @property
    def SE(self) -> Point:
        """return: South-East box Point"""
        return Point(arr=self._coords[6].reshape(1, 2))

    @property
    def NE(self) -> Point:
        """return: North-East widget Point"""
        return Point(arr=self._coords[9].reshape(1, 2))

    @property
    def SW(self) -> Point:
        """return: South-West box Point"""
        return Point(arr=self._coords[3].reshape(1, 2))

    @property
    def N(self) -> Point:
        arr = np.empty((1, 2), dtype=np.float32)
        arr[0, 0] = self._coords[0, 0] + (self._coords[6, 0] - self._coords[0, 0]) * 0.5
        arr[0, 1] = self._coords[0, 1]
        return Point(arr=arr)

    @property
    def S(self) -> Point:
        arr = np.empty((1, 2), dtype=np.float32)
        arr[0, 0] = self._coords[0, 0] + (self._coords[6, 0] - self._coords[0, 0]) * 0.5
        arr[0, 1] = self._coords[3, 1]
        return Point(arr=arr)


class Box(Polygon):
    def validate(self) -> None:
        if len(self._coords) != 2:
            raise ValueError(F"got pair[{len(self._coords)}], expected 2")

    @property
    def size(self) -> Size:
        return Size(arr=(self._coords[1] - self._coords[0]).reshape(1, 2))

    @property
    def base(self) -> Point:
        return Point(arr=self._coords[0].reshape(1, 2))

    @classmethod
    def from_size(cls, size: Size, base: Point = Point(0, 0)) -> Self:
        return cls(arr=np.concatenate((base._coords, (base + size)._coords)))

    def __str__(self) -> str:
        return F"{self.size}{self.base}"

    @property
    def x1(self) -> float:
        return float(self._coords[0][0])

    @property
    def y1(self) -> float:
        return float(self._coords[0][1])

    @property
    def x2(self) -> float:
        return float(self._coords[1][0])

    @property
    def y2(self) -> float:
        return float(self._coords[1][1])

    @property
    def NW(self) -> Point:
        """return: North-West widget Point"""
        return self.base

    @property
    def SE(self) -> Point:
        """return: South-West widget Point"""
        return self.base + self.size

    @property
    def NE(self) -> Point:
        """return: North-East widget Point"""
        return self.base + Point(x=self.size.x)

    @property
    def SW(self) -> Point:
        """return: South-West widget Point"""
        return self.base + Point(y=self.size.y)

    @property
    def N(self) -> Point:
        """return: North widget Point"""
        return self.base + Point(x=self.size.x * 0.5)

    @property
    def S(self) -> Point:
        """return: South widget Point"""
        return self.base + Point(self.size.x * 0.5, self.size.y)

    @property
    def W(self) -> Point:
        """return: West widget Point"""
        return self.base + Point(y=self.size.y * 0.5)

    @property
    def E(self) -> Point:
        """return: East widget Point"""
        return self.base + Point(self.size.x, self.size.y * 0.5)

    def to_smoothbox(self, prop: float = 0.3, maximal: int = 100) -> SmoothBox:
        return SmoothBox.from_size(self.size, self.base, prop, maximal)


class CircleTuple[T]:
    """tuple with circle next/previous methods"""
    __values: tuple[T, ...]
    __pos: int

    def __init__(self, /, *values: T, position: int = 0, value: Optional[T] = None) -> None:
        self.__values = tuple(values)
        if value is not None:
            self.set(value)
        else:
            if position <= len(values):
                self.__pos = position
            else:
                raise ValueError(F"current index more then common values amount")

    @property
    def current(self) -> T:
        return self.__values[self.__pos]

    def next(self) -> T:
        self.__pos += 1
        if self.__pos > len(self.__values) - 1:
            self.__pos = 0
        return self.__values[self.__pos]

    def previous(self) -> T:
        self.__pos -= 1
        if self.__pos < 0:
            self.__pos = len(self.__values) - 1
        return self.current

    def set(self, value: T) -> None:
        self.__pos = self.__values.index(value)


NULL_POLYGON = Polygon(0, 0, 0, 0)
"""use for capture canvas ID"""
