from src.tKot.common import Size, Point, SmoothBox
import timeit


def test_from_size() -> SmoothBox:
    size = Size(100, 100)
    base = Point(0, 0)
    return SmoothBox.from_size(size, base)


def test_from_size_plus_point() -> SmoothBox:
    size = Size(100, 100)
    base = Point(0, 0)
    box = SmoothBox.from_size(size, base)
    return box + Point(1, 1)


n = 10000


create_time = timeit.timeit(test_from_size, number=n)
print(f"SmoothBox.from_size: {create_time/n:.7f} секунд на операцию")

create_plus_time = timeit.timeit(test_from_size_plus_point, number=n)
print(f"SmoothBox.from_size + Point: {create_plus_time/n:.7f} секунд на операцию")
print(f"Разница: {(create_plus_time - create_time)/n:.7f} секунд")