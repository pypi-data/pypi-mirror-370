from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod
import math
import tkinter as tk
from tkinter.font import Font
import numpy as np
from numpy.typing import NDArray
from .common import Point


@dataclass
class ObjListWidget(ABC):
    can: tk.Canvas

    def find_ids(self, e: "tk.Event[tk.Misc]") -> tuple[int, ...]:
        """ find canvas IDs by event. Clear day_info if it not selected """
        y = self.can.canvasy(e.y)
        x = self.can.canvasx(e.x)
        result = self.can.find_overlapping(x-3, y-3, x+3, y+3)
        return result

    @abstractmethod
    def get_event(self, e: "tk.Event[tk.Misc]") -> Optional[int]:
        """"""

    @abstractmethod
    def refresh(self) -> None:
        pass

    @abstractmethod
    def place(self, x: int, y: int) -> None:
        pass


@dataclass
class Vector3phase(ObjListWidget):
    size: Point
    is_1phase: bool = True
    colors: tuple[str, ...] = (
        "#effd5f",
        "#00ff00",
        "#ff0000"
    )

    def __post_init__(self) -> None:
        self.__data: NDArray[np.float32]
        self.__font = Font()
        self.LINE_DEG_COEFS: tuple[float, ...] = (0.35, 0.4)
        self.A = 0
        self.B = 1
        self.C = 2
        self.CUR = 0
        self.VOL = 1
        self.PH = 2
        self.U_LABEL_COEF = 0.48
        self.I_LABEL_COEF = 0.43
        self.__n_phases = 1 if self.is_1phase else 3
        self.__data = np.zeros(
            (self.__n_phases, 4),
            dtype=float
        )
        self.__data[:, 3] = (2/3*math.pi,)*self.__n_phases  # 120 degree
        self.__vectors_cid: list[list[int]] = [[-1, -1] for i in range(self.__n_phases)]
        self.__labels_cid: list[list[int]] = [[-1, -1] for i in range(self.__n_phases)]

    def refresh(self) -> None:
        # normalize i and u vectors
        u_k = (self.size.x*0.35) / np.max(self.__data[:, 1], axis=0, initial=1)
        """normalize coefficient of U"""
        i_k = (self.size.x*0.45) / np.max(self.__data[:, 0], axis=0, initial=1)
        """normalize coefficient of I"""
        angle_offset: float = 0
        for phase in range(len(self.__vectors_cid)):
            i, u, ui_angle, uu_angle = self.__data[phase]
            i_len = i * i_k
            """I vector length in pixels"""
            u_len = u * u_k
            """U vector length in pixels"""
            if phase == self.A:
                uu_angle = 0
            else:
                uu_angle += angle_offset
            angle_offset = uu_angle
            i_angle = uu_angle + ui_angle
            a = self.can.coords(
                self.__vectors_cid[phase][self.VOL],
                self.__center.x, self.__center.y,
                self.__center.x + u_len * math.sin(uu_angle), self.__center.y - u_len * math.cos(uu_angle)
            )
            self.can.coords(
                self.__labels_cid[phase][self.VOL],
                self.__center.x + self.size.x * math.sin(uu_angle) * self.U_LABEL_COEF,
                self.__center.y - math.cos(uu_angle) * self.size.y * self.U_LABEL_COEF
            )
            self.can.coords(
                self.__vectors_cid[phase][self.CUR],
                self.__center.x, self.__center.y,
                self.__center.x + i_len * math.sin(i_angle), self.__center.y - i_len * math.cos(i_angle)
            )
            self.can.coords(
                self.__labels_cid[phase][self.CUR],
                self.__center.x + self.size.x * math.sin(i_angle) * self.I_LABEL_COEF,
                self.__center.y - math.cos(i_angle) * self.size.y * self.I_LABEL_COEF
            )

    def place(self, x: int, y: int) -> None:
        self.__coords = Point(x, y)
        """ x, y image coordinates on canvas """
        colorA, colorB, colorC = self.colors
        self.__center = self.size * 0.5
        self.__cid = self.can.create_rectangle(
            *self.__coords,
            x + self.size.x, y + self.size.y,
            width=0,
            fill="white"
        )
        self.can.create_line(
            x + self.size.x * 0.1, y + self.size.y // 2,
            x + self.size.x * 0.9, y + self.size.y // 2
        )
        self.can.create_line(
            x + self.size.x // 2, y + self.size.y * 0.1,
            x + self.size.x // 2, y + self.size.y * 0.9
        )
        for deg in range(0, 360, 10):
            ang = math.radians(deg)
            self.can.create_line(
                self.__center.x + self.size.x * math.sin(ang) * self.LINE_DEG_COEFS[0], self.__center.y - math.cos(ang) * self.size.y * self.LINE_DEG_COEFS[0],
                self.__center.x + self.size.x * math.sin(ang) * self.LINE_DEG_COEFS[1], self.__center.y - math.cos(ang) * self.size.y * self.LINE_DEG_COEFS[1])
        # create current vectors
        self.__vectors_cid[self.A][self.CUR] = self.can.create_line(
            self.__center.x, self.__center.y,
            self.__center.x, self.__center.y,
            arrow=tk.LAST,
            fill=colorA,
            width=self.size.x // 100,
            dash=(5, 2)
        )
        self.__labels_cid[self.A][self.CUR] = self.can.create_text(
            self.__center.x, self.__center.y,
            font=self.__font,
            text="Ia"
        )
        if len(self.__data) == 3:
            self.__vectors_cid[self.B][self.CUR] = self.can.create_line(
                self.__center.x, self.__center.y,
                self.__center.x, self.__center.y,
                arrow=tk.LAST,
                fill=colorB,
                width=self.size.x // 100,
                dash=(5, 2)
            )
            self.__vectors_cid[self.C][self.CUR] = self.can.create_line(
                self.__center.x, self.__center.y,
                self.__center.x, self.__center.y,
                arrow=tk.LAST,
                fill=colorC,
                width=self.size.x // 100,
                dash=(5, 2)
            )
            self.__labels_cid[self.B][self.CUR] = self.can.create_text(
                self.__center.x, self.__center.y,
                font=self.__font,
                text="Ib"
            )
            self.__labels_cid[self.C][self.CUR] = self.can.create_text(
                self.__center.x, self.__center.y,
                font=self.__font,
                text="Ic"
            )
        # create voltage vectors
        self.__vectors_cid[self.A][self.VOL] = self.can.create_line(
            self.__center.x, self.__center.y,
            self.__center.x, self.__center.y,
            arrow=tk.LAST,
            fill=colorA,
            width=self.size.x // 60)
        self.__labels_cid[self.A][self.VOL] = self.can.create_text(
            self.__center.x, self.__center.y,
            font=self.__font,
            text="Ua"
        )
        if len(self.__data) == 3:
            self.__vectors_cid[self.B][self.VOL] = self.can.create_line(
                self.__center.x, self.__center.y,
                self.__center.x, self.__center.y,
                arrow=tk.LAST,
                fill=colorB,
                width=self.size.x // 60
            )
            self.__vectors_cid[self.C][self.VOL] = self.can.create_line(
                self.__center.x, self.__center.y,
                self.__center.x, self.__center.y,
                arrow=tk.LAST,
                fill=colorC,
                width=self.size.x // 60
            )
            self.__labels_cid[self.B][self.VOL] = self.can.create_text(
                self.__center.x, self.__center.y,
                font=self.__font,
                text="Ub"
            )
            self.__labels_cid[self.C][self.VOL] = self.can.create_text(
                self.__center.x, self.__center.y,
                font=self.__font,
                text="Uc"
            )
        # self.__set_geometry()

    def get_event(self, e: "tk.Event[tk.Misc]") -> int | None:
        raise ValueError(F"not implement in {self.__class__.__name__}")

    """ I(A), U(V), angle(rad)
        for 1ph: I, U, UI_angle
        for 3ph: Ia, Ua, UaIa_angle, UcUa_angle, Ib, Ub, UbIb_angle, UaUb_angle, Ic, Uc, UcIc_angle, UbUc_angle"""

    def set_Ia(self, value: float | int) -> None:
        self.__data[0, 0] = value

    def set_Ua(self, value: float | int) -> None:
        self.__data[0, 1] = value

    def set_UIa_angle(self, value: float | int) -> None:
        self.__data[0, 2] = value

    def set_UcUa_angle(self, value: float | int) -> None:
        self.__data[0, 3] = value

    def set_Ib(self, value: float | int) -> None:
        self.__data[1, 0] = value

    def set_Ub(self, value: float | int) -> None:
        self.__data[1, 1] = value

    def set_UIb_angle(self, value: float | int) -> None:
        self.__data[1, 2] = value

    def set_UaUb_angle(self, value: float | int) -> None:
        self.__data[1, 3] = value

    def set_Ic(self, value: float | int) -> None:
        self.__data[2, 0] = value

    def set_Uc(self, value: float | int) -> None:
        self.__data[2, 1] = value

    def set_UIc_angle(self, value: float | int) -> None:
        self.__data[2, 2] = value

    def set_UbUc_angle(self, value: float | int) -> None:
        self.__data[2, 3] = value
