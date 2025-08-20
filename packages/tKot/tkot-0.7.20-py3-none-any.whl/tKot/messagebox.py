import tkinter as tk
from dataclasses import dataclass, field


@dataclass
class Toast:
    """ short information widget """
    master: tk.Misc
    duration: int = 3000
    color: str = "yellow"
    after_id: str = field(init=False, default="")
    top: tk.Toplevel = field(init=False)

    def call(self, info: str) -> None:
        """ show info with deleting old instance """
        self.top = tk.Toplevel(self.master, width=0, height=0)
        if self.after_id == "":
            self.top.after_cancel(self.after_id)
            self.top.destroy()
        x, y = self.master.winfo_pointerxy()
        self.top.wm_overrideredirect(True)
        self.top.geometry(F"+{x}+{y}")
        tk.Label(self.top, text=info, bg=self.color).pack()
        self.after_id = self.top.after(
            ms=self.duration,
            func=self.top.destroy
        )
