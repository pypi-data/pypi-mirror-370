import os
from pydantic import BaseModel, Field
import tomllib


class _BaseModelEditorHeading(BaseModel):
    name: str = "name"
    value: str = "value"


class _MessageBox(BaseModel):
    title: str
    msg: str


class _ErrorMessages(BaseModel):
    change_valueValueError: _MessageBox = _MessageBox(title="error", msg="Incorrect value")
    change_valueException: _MessageBox = _MessageBox(title="error", msg="It was not possible to save")
    save_settingsException: _MessageBox = _MessageBox(title="error", msg="Saving error")


class _BaseModelEditor(BaseModel):
    title: str = "BaseModelEditor"
    geometry: str = "800x600"
    heading: _BaseModelEditorHeading = Field(default_factory=_BaseModelEditorHeading)
    save: str = "save"
    error_messages: _ErrorMessages = Field(default_factory=_ErrorMessages)
    choise_color: str = "choise_color"


class _Pydantic(BaseModel):
    BaseModelEditor: _BaseModelEditor = Field(default_factory=_BaseModelEditor)


class Settings(BaseModel):
    pydantic: _Pydantic = Field(default_factory=_Pydantic)


if not os.path.isfile(path := ".//config.toml"):
    path = F"{os.path.dirname(__file__)}{path}"
elif os.path.isfile(path):
    with open(path, "rb") as f:
        toml_data = tomllib.load(f)
        data = toml_data.get("tKot", {})
        print(f"Find configuration <config.toml> with path: {f}")
        settings = Settings(**data)
else:
    print("NOT FIND CONFIGURATION: <config.toml>")
    toml_data = {}
    settings = Settings()
