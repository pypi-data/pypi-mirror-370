from imgui_bundle import (
    imgui, hello_imgui, immapp,
    ImVec2, IM_COL32
)

from imgui_builder.components import component, flags_
from imgui_builder.constructors import VertDivision, HorDivision
from imgui_builder.widgets import Text

def main():
    with HorDivision():
        Text('hio')
        Text('hio')

immapp.run(main)