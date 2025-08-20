import tkinter as tk
from src.tKot.buttons import StatusIcon
from src.tKot.common import Size
from PIL import Image


root = tk.Tk()
c = tk.Canvas(root)
c.pack()
on_image = Image.open("./data/relay_on2.png")
off_image = Image.open("./data/relay_off2.png")
un = Image.open("./data/unknown.png")
s_icon = StatusIcon(c, {
    -1: un,
    1: on_image,
    2: off_image},
    default=-1)
s_icon.set_size(Size(100, 100) * .4)
s_icon.place(10, 10)
root.after(2000, lambda: s_icon.set_status(2))
root.after(4000, lambda: s_icon.set_status(1))
root.mainloop()
