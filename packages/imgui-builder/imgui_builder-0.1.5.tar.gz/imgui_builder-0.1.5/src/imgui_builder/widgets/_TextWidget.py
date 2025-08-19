from typing import Literal

from .._base import (
    imgui, ImVec2,
    BaseWidget
)
from ._widgets_utils import get_scope_parent

class Text(BaseWidget):
    def __init__(self, text: str, *, align: Literal['top', 'middle', 'bottom'] | Literal[0, 0.5, 1] = 0) -> None:
        self.text = text
        self.align = align

        parent_layout = get_scope_parent()
        if parent_layout and hasattr(parent_layout, 'new_component'): parent_layout.new_component(component=self)
        elif not parent_layout: self.render()

    def render(self):
        imgui.text(self.text)

    def size(self):
        text_size = imgui.calc_text_size(self.text)
        return ImVec2(text_size.x * 0.8, text_size.y * 0.97)