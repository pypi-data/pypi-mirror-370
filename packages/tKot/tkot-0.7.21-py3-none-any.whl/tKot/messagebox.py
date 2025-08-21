from typing import Optional
import tkinter as tk
from dataclasses import dataclass, field
from .common import Point


@dataclass
class Toast:
    """ short information widget """
    master: tk.Misc
    duration: int = 3000
    color: str = "yellow"
    top: Optional[tk.Toplevel] = field(init=False, default=None)

    def call(self, info: str) -> None:
        """ show info with deleting old instance """
        if self.top:
            self.__destroy()
        self.top = tk.Toplevel(
            master=self.master,
            width=0,
            height=0
        )
        self.top.wm_overrideredirect(True)
        self.top.geometry(str(Point(*self.master.winfo_pointerxy())))
        tk.Label(
            master=self.top,
            text=info,
            bg=self.color
        ).pack()
        self.top.after(
            ms=self.duration,
            func=self.__destroy
        )

    def __destroy(self) -> None:
        if self.top:
            self.top.destroy()
            self.top = None
