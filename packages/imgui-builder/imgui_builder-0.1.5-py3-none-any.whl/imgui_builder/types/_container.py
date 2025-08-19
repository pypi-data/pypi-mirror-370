from typing import Any, Protocol

class Container(Protocol):
    _cls: type
    area: object
    screen: object

    def __getattr__(self, name: Any) -> Any: ...