import tkinter as tk
from src.tKot.messagebox import Toast


def foo(e: "tk.Event[tk.Misc]") -> None:
    toast.call("toast message")


root = tk.Tk()
toast = Toast(root)
toast.call("toast message")
# but = tk.Button(root, text="push")
# but.pack()
root.bind(
    sequence="<Button-3>",
    func=foo
)
root.mainloop()
