from typing import Any, Protocol

class Container(Protocol):
    area: object
    screen: object
    def __getattr__(self, name: Any) -> Any: ...
