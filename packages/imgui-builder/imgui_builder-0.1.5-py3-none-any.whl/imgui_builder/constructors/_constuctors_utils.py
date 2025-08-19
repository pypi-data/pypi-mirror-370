from .._base import imgui
from .._scopes_storage import scopes_parents

def child_id() -> int:
    return len(scopes_parents)

def get_scope_parent() -> object | None:
    current_scope = imgui.get_current_context().current_focus_scope_id
    return scopes_parents.get(current_scope, None)

def set_scope_parent(parent: object):
    current_scope = imgui.get_current_context().current_focus_scope_id
    scopes_parents[current_scope] = parent

# def delete_scope_parent():
#     # No longer used (now AppState.scopes_parent is cleared on every frame instead)
#     current_scope = imgui.get_current_context().current_focus_scope_id
#     del AppState.scopes_parents[current_scope]

def clear_scopes_parents():
    scopes_parents.clear()