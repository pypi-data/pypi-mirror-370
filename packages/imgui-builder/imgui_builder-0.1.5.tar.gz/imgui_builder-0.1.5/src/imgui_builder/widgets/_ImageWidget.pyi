from .._base import BaseWidget as BaseWidget, ImVec2 as ImVec2, hello_imgui as hello_imgui, imgui as imgui
from ._widgets_utils import get_scope_parent as get_scope_parent
from _typeshed import Incomplete
from typing import Literal

class Image(BaseWidget):
    img_path: Incomplete
    img_size: Incomplete
    align: Incomplete
    def __init__(self, img_path: str, img_size: tuple[int | float, int | float], *, align: Literal['top', 'middle', 'bottom'] | Literal[0, None, 1] = 0) -> None: ...
    def render(self) -> None: ...
    def size(self): ...
