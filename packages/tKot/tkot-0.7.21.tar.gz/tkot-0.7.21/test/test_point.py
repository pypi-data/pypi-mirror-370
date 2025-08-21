import unittest
from time import perf_counter
from copy import copy
from src.tKot.common import Polygon, Box, Point, Size, SmoothBox


class TestType(unittest.TestCase):
    def test_Polygon(self) -> None:
        pol = Polygon(4, 0, 24, 0, 24, 4, 13, 4, 13, 9, 10, 9, 10, 33, 27, 33, 27, 9, 13, 9,
                      13, 4, 24, 4, 24, 0, 33, 0, 37, 4, 37, 38, 33, 42, 4, 42, 0, 38, 0, 4)
        self.assertEqual(pol.size, Point(37, 42))
        x = pol.base
        self.assertEqual(pol.base, Point(0, 0))
        pol = pol.reshape(Size(100, 100))
        point = Point(3, 5)
        pol *= Point(2, 1)
        pol += point
        self.assertEqual(pol.base, Point(3, 5))
        print(*pol)

    def test_Box(self) -> None:
        box = Box(1, 1, 10, 10)
        self.assertEqual(str(box), "9x9+1+1")
        box2 = Box.from_size(
            size=Size(10, 10),
            base=Point(2, 2)
        )
        self.assertEqual(str(box2), "10x10+2+2")
        self.assertEqual(box.NE, Point(10, 1))
        self.assertEqual(box.NW, Point(1, 1))
        self.assertEqual(box.SE, Point(10, 10))
        self.assertEqual(box.SW, Point(1, 10))
        self.assertEqual(box.N, Point(5.5, 1))
        self.assertEqual(box.W, Point(1, 5.5))
        self.assertEqual(box.E, Point(10, 5.5))
        self.assertEqual(box.S, Point(5.5, 10))
        self.assertEqual(box.size, Size(9, 9))

    def test_SmoothBox(self) -> None:
        st = perf_counter()
        for _ in range(1000):
            box = SmoothBox.from_size(
                size=Size(100, 100),
                base=Point(20, 10)
            )
        print(perf_counter()-st)
        st = perf_counter()
        for _ in range(1000):
            box = SmoothBox.from_size(
                size=Size(100, 100),
                base=Point(20, 10)
            )
        print(perf_counter()-st)

    def test_init(self) -> None:
        self.assertEqual(Point(), Point(0, 0))
        self.assertRaises(ValueError, Point, (0, 1, 3, 4))
        point = Point(0, 0)
        self.assertEqual(point.x, 0, "compare x")
        self.assertEqual(Point(x=1, y=10), Point(1, 10), "by x, y ordinate")
        size = Size(arr=point._coords)
        self.assertEqual(str(size), "0x0")

    def test_mul(self) -> None:
        p = Size(10, 10)
        self.assertEqual(p * 2, Size(20, 20))

    def test_reduce(self) -> None:
        point = Point(10, 10)
        point2 = Point(100, 100) - point
        self.assertEqual(point2, Point(90, 90))

    def test_add(self) -> None:
        point = Point(10, 10)
        point2 = Point(100, 100) + point
        self.assertEqual(point2, Point(110, 110))
        point._coords.flags.writeable = True
        point.y += 1
        self.assertEqual(point, Point(10, 11))

    def test_unpack(self) -> None:
        point = Point(10, 10)
        x, y = point
        self.assertEqual(x, 10)
        # self.assertEqual(list(point), [10, 10])

    def test_floordiv(self) -> None:
        point = Point(10, 10)
        self.assertEqual(point // 2, Point(5, 5))

    def test_idiv(self) -> None:
        point = Point(10, 10)
        p_div = Point(2, 3)
        res = point / p_div
        self.assertEqual(point // 2, Point(5, 5))

    def test_copy(self) -> None:
        p = Point(10, 10)
        p2 = copy(p)
        p2.x = 20
        print(p, p2)

    def test_size(self) -> None:
        s = Size(0.3, 0.1)
        s2 = s / s.x
        print(s2)