from .._base import imgui

from .._scopes_storage import scopes_parents

def get_scope_parent() -> object | None:
    current_scope = imgui.get_current_context().current_focus_scope_id
    return scopes_parents.get(current_scope, None)
