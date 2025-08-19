from .._base import imgui as imgui
from _typeshed import Incomplete

Flags: Incomplete
TableFlags: Incomplete
WindowFlags: Incomplete

def table_flags_(*flags: _TableFlagName) -> imgui.TableFlags_: ...
def flags_(*flags: _ChildFlagName) -> imgui.ChildFlags_: ...
def window_flags_(*flags: _WindowFlagName) -> imgui.WindowFlags_: ...
