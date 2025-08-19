from .._base import BaseWidget as BaseWidget, ImVec2 as ImVec2, imgui as imgui
from ._widgets_utils import get_scope_parent as get_scope_parent
from _typeshed import Incomplete
from typing import Literal

class Text(BaseWidget):
    text: Incomplete
    align: Incomplete
    def __init__(self, text: str, *, align: Literal['top', 'middle', 'bottom'] | Literal[0, None, 1] = 0) -> None: ...
    def render(self) -> None: ...
    def size(self): ...
