from abc import ABC, abstractmethod

class Container(ABC):
    @abstractmethod
    def __init__(self, container_cls: type, area: object, screen: object) -> None: 
        ...
