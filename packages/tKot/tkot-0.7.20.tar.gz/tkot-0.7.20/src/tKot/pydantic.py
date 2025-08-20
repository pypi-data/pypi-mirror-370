import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
from tkinter import ttk
from typing import Optional, Callable, Any, cast, ClassVar
from pathlib import Path
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema
from .common import Box, Size, Point
from .entries import TopEntry
from .settings import settings


type IID = str


class Color(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )


class BaseModelEditor:
    link: dict[IID, tuple[BaseModel, str]]
    modified: set[IID]
    bool_variables: ClassVar[tuple[str, ...]] = ("No", "Yes")

    def __init__(self, root: tk.Tk, model: BaseModel, cb: Callable[[BaseModel], None]):
        self.top = tk.Toplevel(root)
        self.model = model.model_copy(deep=True)
        self.__cb = cb
        self.link = {}
        self.modified = set()
        self.tree = ttk.Treeview(
            master=self.top,
            columns=("value",)
        )
        self.top.title(settings.pydantic.BaseModelEditor.title)
        self.top.geometry(settings.pydantic.BaseModelEditor.geometry)
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Button(
            btn_frame, text=settings.pydantic.BaseModelEditor.save,
            command=self.save_settings
        ).pack(side=tk.RIGHT, padx=5)
        self.tree.column("#0", width=300, minwidth=100)
        self.tree.column("value", width=200, minwidth=100, anchor=tk.E)
        self.tree.heading("#0", text=settings.pydantic.BaseModelEditor.heading.name)
        self.tree.heading("value", text=settings.pydantic.BaseModelEditor.heading.value, anchor=tk.E)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)
        self.load_settings_to_tree()

    def load_settings_to_tree(self) -> None:
        """Recursively load settings into the treeview"""
        self.tree.delete(*self.tree.get_children())
        self._add_model_to_tree("", self.model)

    def _add_model_to_tree(self, root_iid: IID, root_model: BaseModel) -> None:
        """Iterative method to add model fields to tree using stack"""
        stack = [(root_iid, root_model)]
        while stack:
            parent_iid, model = stack.pop()
            for field_name, field_info in model.model_fields.items():
                submodel = getattr(model, field_name)
                name = field_info.title or field_name
                if isinstance(submodel, BaseModel):
                    node_iid = self.tree.insert(
                        parent_iid,
                        tk.END,
                        text=name,
                        values=("",),
                        tags=("parent",)
                    )
                    stack.append((node_iid, submodel))
                elif isinstance(submodel, list):
                    node_iid = self.tree.insert(
                        parent_iid,
                        tk.END,
                        text=name,
                        values=(f"[{len(submodel)} elements]",),
                        tags=("list",)
                    )
                    for i in range(len(submodel)):
                        item = submodel[i]
                        if isinstance(item, BaseModel):
                            item_iid = self.tree.insert(
                                node_iid,
                                tk.END,
                                text=f"* {i}",
                                values=("",),
                                tags=("list_item",)
                            )
                            stack.append((item_iid, item))
                        else:
                            self.tree.insert(
                                node_iid,
                                tk.END,
                                text=f"Item {i}",
                                values=(str(item),),
                                tags=("list_item",)
                            )
                else:
                    if isinstance(submodel, bool):
                        value = self.bool_variables[int(submodel)]
                    else:
                        value = str(submodel)
                    self.link[self.tree.insert(
                        parent_iid,
                        tk.END,
                        text=name,
                        values=(value,),
                    )] = (model, field_name)

    def on_tree_select(self, event: "tk.Event[tk.Misc]") -> None:
        """Handle selection of a tree item"""
        if not (selected := self.tree.selection()):
            return
        iid = selected[0]
        if res := self.link.get(iid):
            match getattr(*res):
                case Path() as path:
                    if (value := filedialog.askopenfilename(initialdir=path.parent, filetypes=(("DAT", "*.dat"),))) != "":
                        self.change_value(iid, value)
                case Color() as color:
                    val = colorchooser.askcolor(initialcolor=str(color), title=settings.pydantic.BaseModelEditor.choise_color)
                    if (value := val[1]) is not None:
                        self.change_value(iid, value)
                # case bool():
                #     print("")
                case _:
                    if isinstance(res2 := self.tree.bbox(iid, column="value"), tuple):
                        x_e, y_e, w, h = res2
                        x, y = self.tree.winfo_rootx() + x_e, self.tree.winfo_rooty() + y_e
                        TopEntry[IID](
                            master=self.top,
                            box=Box.from_size(
                                size=Size(w, h),
                                base=Point(x, y)
                            ),
                            desc=iid,
                            value=self.tree.item(selected[0])["values"][0],
                            callback=self.change_value
                        )
                    else:
                        raise RuntimeError(f"not find {iid} in tree")

    def _keep_item(self, iid: IID, value: str) -> None:
        self.tree.item(iid, values=(value,))
        self.modified.add(iid)

    def change_value(self, iid: IID, value: str) -> bool:
        """Save the edited value back to the settings model with full type support"""
        item_tags = self.tree.item(iid, "tags")
        try:
            if iid in self.link:
                model, field_name = self.link[iid]
                field_info = model.model_fields[field_name]
                if not field_info.annotation:
                    return False
                converted_value = self._convert_value(value, field_info.annotation)
                setattr(model, field_name, converted_value)
                self._keep_item(iid, str(converted_value))
                return True
            elif item_tags and "list_item" in item_tags:
                parent_id = self.tree.parent(iid)
                if parent_id in self.link:
                    model, field_name = self.link[parent_id]
                    lst = getattr(model, field_name)
                    idx = self._get_item_index(iid)
                    if idx is not None and 0 <= idx < len(lst):
                        field_type = type(lst[idx]) if idx < len(lst) else str
                        lst[idx] = self._convert_value(value, field_type)
                        self._keep_item(iid, str(lst[idx]))
                    return True
                return False
        except ValueError as e:
            messagebox.showerror(
                settings.pydantic.BaseModelEditor.error_messages.change_valueValueError.title,
                F"{settings.pydantic.BaseModelEditor.error_messages.change_valueValueError.msg}: {str(e)}"
            )
        except Exception as e:
            messagebox.showerror(
                settings.pydantic.BaseModelEditor.error_messages.change_valueException.title,
                f"{settings.pydantic.BaseModelEditor.error_messages.change_valueException.msg}: {str(e)}")
        return False

    def _convert_value[T](self, value: str, target_type: type[T]) -> T:
        """Convert string value to target type"""
        if target_type is bool:
            return cast("T", value.lower() in ("true", "1", "yes", "да"))
        return target_type(value)

    def _get_item_index(self, item_id: IID) -> Optional[int]:
        """Extract index from list item text (e.g. 'Item 0' -> 0)"""
        item_text = self.tree.item(item_id, "text")
        if item_text.startswith(("Item ", "* ")):
            try:
                return int(item_text.split()[-1])
            except (IndexError, ValueError):
                return None
        return None

    def save_settings(self) -> None:
        try:
            self.model.model_validate(self.model.dict())
            self.__cb(self.model)
        except Exception as e:
            messagebox.showerror(
                settings.pydantic.BaseModelEditor.error_messages.save_settingsException.title,
                f"{settings.pydantic.BaseModelEditor.error_messages.save_settingsException.msg}: {str(e)}")
            return None
