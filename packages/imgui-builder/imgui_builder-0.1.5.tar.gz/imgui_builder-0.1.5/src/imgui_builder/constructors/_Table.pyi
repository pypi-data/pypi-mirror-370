import types
from .._base import BaseWidget as BaseWidget, ImVec2 as ImVec2, imgui as imgui
from ._constuctors_utils import child_id as child_id, get_scope_parent as get_scope_parent, set_scope_parent as set_scope_parent
from typing import Literal, NotRequired, TypedDict, Unpack

class TableArgs(TypedDict):
    flags: NotRequired[imgui.TableFlags_]
    outer_size: NotRequired[ImVec2]
    inner_width: NotRequired[float]

class Table:
    def __init__(self, size: tuple[int, int] = (0, 0), *, columns: Literal[2, 3, 4, 5, 6] = 2, **kwargs: Unpack[TableArgs]) -> None: ...
    container_creation_success: bool
    def __enter__(self): ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: types.TracebackType | None) -> None: ...
