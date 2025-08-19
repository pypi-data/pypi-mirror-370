from typing import Any, Dict, List, Tuple, TypedDict, Unpack, Literal, NotRequired, Optional, Callable

from .._base import (
    imgui, ImVec2,
    BaseWidget
)
from ._constuctors_utils import child_id, get_scope_parent, set_scope_parent

class TableArgs(TypedDict):
    flags: NotRequired[imgui.TableFlags_]
    outer_size: NotRequired[ImVec2]
    inner_width: NotRequired[float]
    
class Table:
    def __init__(self, size: Tuple[int, int] = (0, 0), *, columns: Literal[2, 3, 4, 5, 6] = 2, **kwargs: Unpack[TableArgs]):
        self._parent = get_scope_parent()
        self._size = self._get_size(size) #* Если у текущего layout нет родителя, то он будет использовать свой переданный размер `size`, если родитель есть, то он будет использовать размер `flexbox` родителя как свой размер (или же так же свой, если его нет)

        self._columns = columns
        self._kwargs = kwargs

        self._container_creation_success = False
        self._rows: List[Dict[int, Any]] = []

    def __enter__(self):
        if self._columns < 2: raise ValueError("У теблицы должны быть хотя бы 2 колоны, иначе используйте vertical/horizontal layouts")

        if imgui.begin_child(f'table child {child_id()}', self._size):
            if imgui.begin_table(f'table {child_id()}', **{'columns': self._columns, **self._kwargs}):
                self.container_creation_success = True

                set_scope_parent(parent=self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.container_creation_success: return

        #* Начинаем создавать таблицу только когда выходим из контекстного менеджера таблицы, чтобы кол-во строк уже было известно
        # Looping through all the row columns, adding widget/layout if needed, or just skipping that column
        for row_num, (row_flags, row_cols) in enumerate(self._rows):
            row_size_y = self._size.y / len(self._rows) - 4
            imgui.table_next_row(row_flags=row_flags, min_row_height=row_size_y)

            for col_num in range(self._columns):
                element = row_cols.get(col_num)

                imgui.table_next_column()
                if not element: continue

                imgui.begin_child(f'table cell {row_num} {col_num} {child_id()}', ImVec2(imgui.get_content_region_avail().x, row_size_y))
                self._add_col_element(element=element)
                imgui.end_child()

        #* Заканчиваем таблицу
        imgui.end_table()
        imgui.end_child()

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

    def _add_row(self, 
            *cols_elements: BaseWidget | Callable, col_positioned_elements: Optional[Dict[int, BaseWidget | Callable]],
            row_flags: imgui.TableRowFlags_ = 0
        ):
        if cols_elements and col_positioned_elements:
            raise ValueError("Ты можешь либо передать *колонки по порядку, либо позиционированные колоны, но не их оба!")

        # Using dict col_positioned_elements or converting *cols_elements to a needed format {col_num: element}
        cols_elements: Dict[int, BaseWidget | Callable] = col_positioned_elements or {col_num: element for col_num, element in enumerate(cols_elements)}

        self._rows.append((row_flags, cols_elements))

    def _add_col_element(self, element: BaseWidget | Callable):
        element() if callable(element) else element.render() 