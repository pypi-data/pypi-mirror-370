import tkinter as tk
from src.tKot.entries import TopEntry
from src.tKot.common import Box, Size, Point


def cb(desc: list[str], value: str) -> bool:
    if value != "test":
        raise ValueError("not test")
    print(desc, value)
    return True


root = tk.Tk()
x: TopEntry[list[str]] = TopEntry(
    master=root,
    box=Box.from_size(
        size=Size(200, 20),
        base=Point(100, 200)
    ),
    desc=['1.2.3.4.5.6', '1'],
    value="test",
    callback=cb
)
root.mainloop()
