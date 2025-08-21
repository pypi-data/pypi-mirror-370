import math
import tkinter as tk
import numpy as np
from src.tKot.common import Point
from src.tKot.diagram import Vector3phase


def update_data() -> None:
    try:
        i = next(it)
    except StopIteration:
        return
    print(i)
    d.set_UIa_angle(i)
    d.refresh()
    root.after(100, update_data)


root = tk.Tk()
can = tk.Canvas()
can.pack()
d = Vector3phase(
    can=can,
    size=Point(200, 200),
    is_1phase=False
)
d.place(0, 0)
d.set_Ua(100)
d.set_Ia(5)
d.set_Ub(200)
d.set_Ib(3)
d.set_UIb_angle(.1)
d.set_Uc(220)
d.set_Ic(2)
d.set_UIc_angle(.1)
it = iter(np.arange(0, math.pi*2, .1))
root.after(2000, update_data)
root.mainloop()
