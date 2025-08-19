from .._base import BaseWidget as BaseWidget, imgui as imgui
from ._widgets_utils import get_scope_parent as get_scope_parent
from typing import Callable, overload

class Row:
    @overload
    def __init__(self, *, rows_flags: imgui.TableRowFlags_ = 0, min_row_height: float = 0.0) -> None: ...
    @overload
    def __init__(self, *cols_elements: BaseWidget | Callable, col_positioned_elements: dict[int, BaseWidget | Callable] | None = None, row_flags: imgui.TableRowFlags_ = 0, min_row_height: float = 0.0) -> None: ...
