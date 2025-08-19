from .._base import (
    imgui, ImVec2,
    BaseWidget
)
from ._widgets_utils import get_scope_parent

class Spacing(BaseWidget):
    def __init__(self, offset: int | float) -> None:
        self.parent_layout = get_scope_parent()
        self.dummy_size = ImVec2(
            offset if self.parent_layout.layout_type == 'horizontal' else 0,
            offset if self.parent_layout.layout_type == 'vertical' else 0
        )

        if self.parent_layout: self.parent_layout.new_component(component=self)
        else: self.render()

    def render(self):
        imgui.dummy(self.dummy_size)

    def size(self):
        return self.dummy_size