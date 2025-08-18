from pathlib import Path

from htmltools import HTMLDependency, TagList
from htmltools._core import HTMLDependencySource, ScriptItem, StylesheetItem
from shiny import ui
from shiny.module import resolve_id

assets_dir = Path(__file__).parent / "assets"

coloris_dependency = HTMLDependency(
    name="coloris",
    version="0.21.1",  # Use the version of Coloris you downloaded
    source=HTMLDependencySource(package="shiny_coloris", subdir="assets"),
    script=[ScriptItem(src="coloris.min.js")],
    stylesheet=StylesheetItem(href="coloris.min.css"),
)


def color_input(id: str, label: str, value: str = "#000000") -> TagList:
    """
    Creates a Coloris color picker input control.

    :param id: The input slot that will be used to access the value.
    :param label: The display label for the control.
    :param value: The initial color value.
    """
    return TagList(
        coloris_dependency,
        ui.div(
            ui.tags.style("""
                    .clr-picker {
                        z-index: 1150;
                    } /*Modal in shiny is at 1055. Without this, the
                      color picker appears behind the modal, which is not ideal (useless) */
                    /*.shiny-custom-coloris-picker {
                      width: 120px;
                    } */
                """),
            ui.tags.label(label, _for=id),
            ui.div(
                ui.tags.input(
                    type="text",
                    id=resolve_id(id),
                    class_="shiny-custom-coloris-picker",
                    **{"data-coloris": ""},
                    value=value,
                ),
                ui.HTML("<button>::after</button>"),
                class_="clr-field",
                style=f"padding: 2px; border: 1px solid #cccccc; border-radius: 1px;color:{value}",
            ),
            style="display: flex; align-items: center; gap: 10px; justify-content: space-between; margin-bottom: 10px;",
        ),
    )
