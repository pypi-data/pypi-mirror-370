from abc import ABC, abstractmethod
from typing import Any

from . import ImVec2

class BaseWidget(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def size(self) -> ImVec2:
        pass

class BaseLayout(ABC):
    layout_type: str

    @abstractmethod
    def __init__():
        pass
    
    @abstractmethod
    def __enter__(self) -> Any:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @abstractmethod
    def _align_component(self, align_type, comp_size):
        pass

    @abstractmethod
    def new_component(self, component):
        pass

class BaseContainer(ABC):
    @abstractmethod
    def __init__(self):
        pass