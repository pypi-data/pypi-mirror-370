import tkinter as tk
from src.tKot.entries import TopListBox
from src.tKot.common import Box, Size, Point


def cb(desc: list[str], value: str) -> bool:
    if value != "test":
        raise ValueError("not test")
    print(desc, value)
    return True


def foo():
    TopListBox(
        master=root,
        box=Box.from_size(
            size=Size(200, 100),
            base=Point(100, 200)
        ),
        desc=['1.2.3.4.5.6', '1'],
        value="test",
        values=("test", "a", "b"),
        callback=cb
    )


root = tk.Tk()
tk.Button(root, text="push", command=foo).pack()
root.mainloop()
