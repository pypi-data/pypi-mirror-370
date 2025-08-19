import abc
import types
from . import ImVec2 as ImVec2
from abc import ABC, abstractmethod
from typing import Any

class BaseWidget(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self): ...
    @abstractmethod
    def render(self): ...
    @abstractmethod
    def size(self) -> ImVec2: ...

class BaseLayout(ABC, metaclass=abc.ABCMeta):
    layout_type: str
    @abstractmethod
    def __init__(): ...
    @abstractmethod
    def __enter__(self) -> Any: ...
    @abstractmethod
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: types.TracebackType | None): ...
    @abstractmethod
    def new_component(self, component): ...

class BaseContainer(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self): ...
