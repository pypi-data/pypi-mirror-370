from .._base import BaseWidget as BaseWidget, ImVec2 as ImVec2, imgui as imgui
from ._widgets_utils import get_scope_parent as get_scope_parent
from _typeshed import Incomplete

class Spacing(BaseWidget):
    parent_layout: Incomplete
    dummy_size: Incomplete
    def __init__(self, offset: int | float) -> None: ...
    def render(self) -> None: ...
    def size(self): ...
