from src.tKot import Icon
from PIL import Image
import tkinter as tk
from data import images

root = tk.Tk()
but: Icon = Icon(
    master=root,
    pillow_image=Image.frombytes('RGB', (100, 100), images.connected),
    # with_fix=True,
    text="message",
    height=40  # need for pack
)
# but.place(relx=0.1, rely=0.1, relheight=0.8)
but.pack(side=tk.LEFT)
but2 = Icon(master=root,
            pillow_image=Image.frombytes('RGB', (100, 100), images.connected),
            with_fix=True,
            text="message",
            height=40  # need for pack
            )
but2.pack(side=tk.LEFT)
root.mainloop()
