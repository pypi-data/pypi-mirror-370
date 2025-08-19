from typing import Any, Callable

def component(func: Callable[..., Any]) -> Callable[..., Callable[[], Any]]:

    def wrapper(*args: Any, **kwargs: Any) -> Callable[[], Any]:
        return lambda: func(*args, **kwargs)

    return wrapper