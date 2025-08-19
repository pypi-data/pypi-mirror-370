from typing import Optional, overload, Callable

from .._base import (
    imgui,
    BaseWidget
)
from ._widgets_utils import get_scope_parent

class Row:
    @overload
    def __init__(self, 
        *,
        rows_flags: imgui.TableRowFlags_ = 0, min_row_height: float = 0.0
    ): ...

    @overload
    def __init__(self, 
        *cols_elements: BaseWidget | Callable, col_positioned_elements: Optional[dict[int, BaseWidget | Callable]] = None,
        row_flags: imgui.TableRowFlags_ = 0, min_row_height: float = 0.0
    ): ...

    def __init__(self, 
            *cols_elements: BaseWidget | Callable, col_positioned_elements: Optional[dict[int, BaseWidget | Callable]] = None, 
            row_flags: imgui.TableRowFlags_ = 0, min_row_height: float = 0.0
        ):
        
        table_parent = get_scope_parent()

        table_parent._add_row(*cols_elements, col_positioned_elements=col_positioned_elements, row_flags=row_flags)
