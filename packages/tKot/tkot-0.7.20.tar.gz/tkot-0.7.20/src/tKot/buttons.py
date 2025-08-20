from typing import Optional, Any
import tkinter as tk
from PIL import Image, ImageTk
from .common import Size


class Icon(tk.Widget):
    p_im: Image.Image | None
    im: Optional[ImageTk.PhotoImage]
    info: Optional[str]

    def __init__(self, master: Optional[tk.Misc] = None, **kw: Any) -> None:
        self.p_im = kw.pop("pillow_image", None)
        if kw.pop("radio", False):
            tk.Widget.__init__(self, master, 'radiobutton', kw)
            kw["indicatoron"] = True
        elif kw.pop("with_fix", None):
            kw["indicatoron"] = False
            tk.Widget.__init__(self, master, "checkbutton", kw)
        else:
            tk.Widget.__init__(self, master, "button", kw)
        self.im = None
        self.bind("<Configure>", self.__handle_configure)

    def __handle_configure(self, e: "tk.Event[tk.Misc]") -> None:
        """auto change image size"""
        if self.p_im:
            h = self.winfo_height()
            """current button height"""
            self.im = ImageTk.PhotoImage(self.p_im.resize((h, h)))
            self.configure(image=self.im, width=h)


class StatusIcon:
    """Icon with status properties"""
    __c: tk.Canvas
    __current: int
    __im: ImageTk.PhotoImage
    __size: Size
    __images: dict[int, Image.Image]

    def __init__(self,
                 canvas: tk.Canvas,
                 images: dict[int, Image.Image],
                 default: Optional[int] = None) -> None:
        self.__c = canvas
        """ canvas for widget """
        self.__c_id = -1
        """ Image canvas ID. -1 if not place """
        self.__images = images
        self.__size = Size(100, 100)
        """icon size"""
        self.set_status(tuple(self.__images.keys())[0] if default is None else default)

    def get_status(self) -> int:
        """return current status"""
        return self.__current

    def __set_image(self) -> None:
        self.__im = ImageTk.PhotoImage(self.__images[self.__current].resize((int(self.__size.x), int(self.__size.y))))

    def set_status(self, value: int) -> None:
        """set status with change image"""
        self.__current = value
        self.__set_image()
        if self.__c_id != -1:
            self.__c.itemconfigure(self.__c_id, image=self.__im)

    def set_size(self, value: Size) -> None:
        if self.__c_id == -1:
            self.__size = value
            self.__set_image()
        else:
            raise ValueError(F"need clear from canvas before set_size")

    @property
    def size(self) -> Size:
        return self.__size

    def place(self, x: int, y: int) -> None:
        """ replace on canvas by (x, y). Old canvas id shall delete"""
        if self.__c_id != -1:
            self.__c.delete(self.__c_id)
        self.__c_id = self.__c.create_image(x, y,
                                            anchor=tk.NW,
                                            image=self.__im)

    def delete(self) -> None:
        """delete from canvas"""
        self.__c.delete(self.__c_id)
        self.__c_id = -1

    @property
    def c_id(self) -> int:
        return self.__c_id
