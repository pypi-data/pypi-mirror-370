from typing import Tuple, Literal

from .._base import (
    imgui, hello_imgui, ImVec2,
    BaseWidget
)
from ._widgets_utils import get_scope_parent

class Image(BaseWidget):
    def __init__(self, img_path: str, img_size: Tuple[int | float, int | float], *, align: Literal['top', 'middle', 'bottom'] | Literal[0, 0.5, 1] = 0) -> None:
        self.img_path = img_path
        self.img_size = ImVec2(*img_size) if img_size[0] != 0 and img_size[1] != 0 else imgui.get_content_region_avail()
        self.align = align
        
        parent_layout = get_scope_parent()
        if parent_layout and hasattr(parent_layout, 'new_component'): parent_layout.new_component(component=self)
        elif not parent_layout: self.render()

    def render(self):
        texture = hello_imgui.im_texture_id_from_asset(self.img_path)
        imgui.image(texture, self.img_size)

    def size(self):
        return self.img_size