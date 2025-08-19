import types
from .._base import BaseLayout as BaseLayout, BaseWidget as BaseWidget, ImVec2 as ImVec2, imgui as imgui
from ..components import Flexbox as Flexbox
from ._constuctors_utils import child_id as child_id, clear_scopes_parents as clear_scopes_parents, get_scope_parent as get_scope_parent, set_scope_parent as set_scope_parent
from typing import Literal, NotRequired, TypedDict, Unpack

class HorDivisionArgs(TypedDict):
    flags: NotRequired[imgui.ChildFlags_]
    window_flags: NotRequired[imgui.WindowFlags_]

class HorDivision(BaseLayout):
    layout_type: str
    def __init__(self, size: tuple[int, int] = (0, 0), *, flexbox: Flexbox | None = None, align: Literal['top', 'middle', 'bottom'] | float = 0, parent_relative_alignment: Literal['left', 'middle', 'right'] | float = 0, **kwargs: Unpack[HorDivisionArgs]) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: types.TracebackType | None) -> None: ...
    @property
    def content_region(self): ...
    def new_component(self, component: BaseWidget | BaseLayout): ...
