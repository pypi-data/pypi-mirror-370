from typing import Literal

from .._base import imgui

#* Type hints
_TableFlagName = Literal[
    "resizable",
    "reorderable",
    "hideable",
    "sortable",
    "no_saved_settings",
    "context_menu_in_body",
    "row_bg",
    "borders_inner_h",
    "borders_outer_h",
    "borders_inner_v",
    "borders_outer_v",
    "borders_h",
    "borders_v",
    "borders_inner",
    "borders_outer",
    "borders",
    "no_borders_in_body",
    "no_borders_in_body_until_resize",
    "sizing_fixed_fit",
    "sizing_fixed_same",
    "sizing_stretch_prop",
    "sizing_stretch_same",
    "no_host_extend_x",
    "no_host_extend_y",
    "prefer_outer_size_x",
    "no_keep_columns_visible",
    "precise_widths",
    "no_clip",
    "pad_outer_x",
    "no_pad_outer_x",
    "no_pad_inner_x",
    "scroll_x",
    "scroll_y",
    "sort_multi",
    "sort_tristate"
]

_ChildFlagName = Literal[
    "border",
    "always_auto_resize",
    "resize_x",
    "resize_y",
    "auto_resize_x",
    "auto_resize_y",
    "frame_style",
    "no_scrollbar",
    "horizontal_scrollbar"
]

_WindowFlagName = Literal[
    "no_title_bar",
    "no_resize",
    "no_move",
    "no_scrollbar",
    "no_scroll_with_mouse",
    "no_collapse",
    "always_auto_resize",
    "no_background",
    "no_saved_settings",
    "no_mouse_inputs",
    "menu_bar",
    "horizontal_scrollbar",
    "no_focus_on_appearing",
    "no_bring_to_front_on_focus",
    "always_vertical_scrollbar",
    "always_horizontal_scrollbar",
    "no_nav_inputs",
    "no_nav_focus",
    "unsaved_document",
    "no_docking",
    "no_decoration",
    "no_inputs"
]

#* Actually exported objects
Flags = imgui.ChildFlags_
TableFlags = imgui.TableFlags_
WindowFlags = imgui.WindowFlags_

def table_flags_(*flags: _TableFlagName) -> imgui.TableFlags_:
    flags_ = imgui.TableFlags_(0)

    for flag in flags:
        flags_ |= getattr(imgui.TableFlags_, flag)

    return flags_

def flags_(*flags: _ChildFlagName) -> imgui.ChildFlags_:
    flags_ = imgui.ChildFlags_(0)

    for flag in flags:
        flags_ |= getattr(imgui.ChildFlags_, flag)

    return flags_

def window_flags_(*flags: _WindowFlagName) -> imgui.WindowFlags_:
    flags_ = imgui.WindowFlags_(0)

    for flag in flags:
        flags_ |= getattr(imgui.WindowFlags_, flag)

    return flags_