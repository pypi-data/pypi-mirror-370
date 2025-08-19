import abc
from abc import ABC, abstractmethod

class Container(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self, container_cls: type, area: object, screen: object): ...
