import tkinter as tk
from typing import Callable, Any, Literal, Collection
from .common import Box


class TopEntry[T]:
    def __init__(self,
                 master: tk.Misc,
                 box: Box,
                 desc: T,
                 value: str,
                 callback: Callable[[T, str], bool],
                 selection: Literal["ON", "OFF"] = "OFF",
                 cursor_pos: Literal["START", "END"] = "START"
                 ) -> None:
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)
        self.top.bind("<FocusOut>", lambda e: self.top.destroy())
        self.top.geometry(str(box))
        self.desc = desc
        """descriptor"""
        self.variable = tk.StringVar(
            master=self.top,
            value=value)
        self.entry = tk.Entry(
            master=self.top,
            textvariable=self.variable,
            justify=tk.RIGHT
        )
        self.entry.bind("<Return>", self.__set_value)
        self.entry.bind("<Escape>", lambda e: self.top.destroy())
        self.entry.pack(
            fill=tk.X
        )
        self.cb = callback
        self.top.lift(master)
        self.entry.focus_set()
        if selection == "ON":
            self.entry.selection_range(0, tk.END)
        if cursor_pos == "START":
            self.entry.icursor(tk.END)

    def __set_value(self, _: "tk.Event[tk.Misc]") -> None:
        try:
            self.cb(self.desc, self.variable.get())
            self.top.destroy()
        except ValueError as e:
            self.entry.configure(background="red")
            self.variable.set(str(e))


class TopOptionMenu[T]:
    o_m: tk.OptionMenu

    def __init__(self,
                 master: tk.Misc,
                 w: int, h: int,
                 x: int, y: int,
                 desc: T,
                 value: str,
                 values: list[str],
                 callback: Callable[[T, str], bool]) -> None:
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)
        self.top.bind("<FocusOut>", lambda e: self.top.destroy())
        self.top.geometry(F"{w}x{h}+{x}+{y}")
        self.desc = desc
        """descriptor"""
        self.var = tk.StringVar(
            master=self.top,
            value=value)
        self.var.trace_add("write", self.__change_var)
        o_m = tk.OptionMenu(
            self.top,
            self.var,
            *values)
        # self.o_m.bind("<Return>", self.__set_value)
        o_m.bind("<Escape>", lambda e: self.top.destroy())
        o_m.pack(
            fill=tk.X
        )
        self.cb = callback
        self.top.lift(master)
        o_m.focus_set()

    def __change_var(self, *args: Any) -> None:
        try:
            self.cb(self.desc, self.var.get())
            self.top.destroy()
        except ValueError as e:
            self.o_m.configure(background="red")
            self.var.set(str(e))

    def __set_value(self, e: "tk.Event[tk.Misc]") -> None:
        try:
            self.cb(self.desc, self.var.get())
            self.top.destroy()
        except ValueError as e:
            self.o_m.configure(background="red")
            self.var.set(str(e))


class TopListBox[T]:
    sc: tk.Scrollbar
    l_b: tk.Listbox

    def __init__(self,
                 master: tk.Misc,
                 box: Box,
                 desc: T,
                 value: str,
                 values: Collection[str],
                 callback: Callable[[T, str], bool]) -> None:
        self.top = tk.Toplevel(master)
        self.top.overrideredirect(True)
        self.top.bind("<FocusOut>", lambda e: self.top.destroy())
        self.top.geometry(str(box))
        self.desc = desc
        """descriptor"""
        self.values = values
        sc = tk.Scrollbar(
            master=self.top,
            orient=tk.VERTICAL)
        self.l_b = tk.Listbox(
            self.top,
            listvariable=tk.Variable(value=values),
            yscrollcommand=sc.set)
        sc.configure(command=self.l_b.yview)
        self.l_b.bind("<Double-Button-1>", self.__set_value)
        self.l_b.bind("<Return>", self.__set_value)
        self.l_b.bind("<Escape>", lambda e: self.top.destroy())
        self.l_b.pack(
            side=tk.LEFT,
            expand=1,
            fill=tk.BOTH)
        sc.pack(
            side=tk.RIGHT,
            fill=tk.Y)
        self.cb = callback
        self.top.lift(master)
        self.l_b.focus_set()
        index = list(values).index(value)
        self.l_b.selection_set(index)
        self.l_b.activate(index)
        self.l_b.see(index)

    def __set_value(self, e: "tk.Event[tk.Misc]") -> None:
        if isinstance(e.widget, tk.Listbox):
            try:
                w = e.widget
                if len(v := w.curselection()) == 1:
                    self.cb(self.desc, self.values[v[0]])
                    self.top.destroy()
                print(v)
            except ValueError as e:
                self.l_b.configure(background="red")
                # self.var.set(str(e))
        else:
            raise RuntimeError("not support")
