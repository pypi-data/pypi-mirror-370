from typing import TypedDict, Unpack, Literal, NotRequired, Optional, Tuple

from .._base import (
    imgui, ImVec2,
    BaseWidget, BaseLayout
)
from ..components import Flexbox
from ._constuctors_utils import child_id, get_scope_parent, set_scope_parent, clear_scopes_parents

class VertDivisionArgs(TypedDict):
    flags: NotRequired[imgui.ChildFlags_]
    window_flags: NotRequired[imgui.WindowFlags_]
    
class VertDivision(BaseLayout):
    layout_type = 'vertical'

    def __init__(self, size: Tuple[int, int] = (0, 0), *, flexbox: Optional[Flexbox] = None, align: Literal['left', 'middle', 'right'] | float = 0, parent_relative_alignment: Literal['top', 'middle', 'bottom'] | float = 0, **kwargs: Unpack[VertDivisionArgs]): 
        self._flexbox = flexbox(
            parent_layout=self.layout_type,
            parent_layout_size=size if size != (0, 0) else (imgui.get_content_region_avail().x, imgui.get_content_region_avail().y) #* Если size установлен на (0, 0), то это значит, что будет использоваться размер доступного контента - мы это и передаем flexbox вместо (0, 0)
        ) if flexbox else None #* Если `flexbox` передан, то данный layout будет считаться ориентиром для нижних layout-ов, и нижнии layout-ты будут использовать размер `flexbox` текущего layout-а как их размер

        self._parent = get_scope_parent()
        self._size = self._get_size(size) #* Если у текущего layout нет родителя, то он будет использовать свой переданный размер `size`, если родитель есть, то он будет использовать размер `flexbox` родителя как свой размер (или же так же свой, если его нет)

        self._kwargs = {'child_flags': kwargs.pop('flags', 0), **kwargs}
        self._align = align
        self._parent_relative_alignment = parent_relative_alignment
        
        self._container_creation_success = False

    def __enter__(self):
        if self._parent and hasattr(self._parent, 'new_component'):
            self._parent.new_component(component=self)
        
        if imgui.begin_child(f'vertical_layout {child_id()}', **{'size': self._size, **self._kwargs}):
            self._container_creation_success = True #! think if it is needed

            set_scope_parent(parent=self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._container_creation_success:
            imgui.end_child()
            if not self._parent: clear_scopes_parents() #* Если это начальное layout

    @property
    def content_region(self):
        return imgui.get_content_region_avail()

    def new_component(self, component: BaseWidget | BaseLayout):
        match component.__class__.__base__.__name__:  # pyright: ignore[reportOptionalMemberAccess]
            case 'BaseWidget':
                self._align_component(getattr(component, 'align', None), component.size())
                component.render()
            case 'BaseLayout':
                self._align_component(component._parent_relative_alignment, component._size)
            case _:
                raise Exception('Wrong component type passed to "new_component"')

    def _get_size(self, given_size: Tuple[int, int]):
        '''
        Динамически возвращает необходимый размер текущего layout\n
        Если у текущего layout есть родитель, и у родителя указан flexbox, возвращается flexbox.size родителя\n
        Если нет, то возвращает переданный `given_size`
        '''
        if self._parent and getattr(self._parent, '_flexbox', None) != None:
            size = self._parent._flexbox.elements_size
            return ImVec2(size[0], size[1])

        return ImVec2(*given_size)

    def _align_component(self, align_type: str | float | None, comp_size: ImVec2):
        content_region_x = imgui.get_content_region_max().x

        match align_type or self._align: # if align_type is not passed, using global one           # pyright: ignore[reportUnknownMemberType]
            case 'left':
                imgui.set_cursor_pos_x(0)
            case 'middle':
                imgui.set_cursor_pos_x(content_region_x / 2 - comp_size.x)
            case 'right':
                imgui.set_cursor_pos_x(content_region_x - comp_size.x)
            case int() | float() as align:
                imgui.set_cursor_pos_x(max((content_region_x / 100) * (align * 100) - comp_size.x, 0)) 
            case _: pass