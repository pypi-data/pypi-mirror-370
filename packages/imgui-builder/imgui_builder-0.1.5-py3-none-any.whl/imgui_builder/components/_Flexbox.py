from typing import Literal, Tuple

class Flexbox:
    '''
    Компонент, используемый для расположения внутренних элементов внутри `layout`, к которому он принадлежит.\n
    `mode` и `elements_count` указывается при иницилизации.\n
    `parent` указывается при вызове обьекта класса (__call__).
    '''

    def __init__(self, mode: Literal['auto'], elements_count: int) -> None:
        self._mode = mode
        self._elements_count = elements_count
        self._parent_layout_size: Tuple[float, float]

        # Exported variable based on which layout is going to position its elements
        self.elements_size: Tuple[float, float] = 0, 0

    def __call__(self, parent_layout: str, parent_layout_size: Tuple[float, float]):
        self._parent_layout_size = parent_layout_size

        # Running needed mode type function to change self.element_size
        needed_method = getattr(self, f'_{parent_layout}_{self._mode}')
        needed_method()

        return self

    #* MODES METHODS - задача любого из этого метода установить размер внутренних элементов
    def _vertical_auto(self):
        # x size - не меняется, y size - делится на количество элементов
        self.elements_size = self._parent_layout_size[0], self._parent_layout_size[1] / self._elements_count
    
    def _horizontal_auto(self):
        # x size - делится на количество элементов, y size - не меняется
        self.elements_size = self._parent_layout_size[0] / self._elements_count, self._parent_layout_size[1]
