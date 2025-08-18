from shiny import App, Inputs, Outputs, Session, reactive, render, ui

from shiny_coloris import color_input

app_ui = ui.page_fluid(
    ui.h2("My Custom Color Picker Module"),
    # It's this easy to use now!
    color_input(id="my_color_1", label="Primary Color:", value="#0d6efd"),
    color_input(id="my_color_2", label="Accent Color:", value="#ffc107"),
    ui.hr(),
    ui.output_text_verbatim("selected_colors"),
    ui.input_action_button("open_modal", "Open Modal"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    reactive_color = reactive.Value("#FF00FF")

    @output
    @render.text
    def selected_colors() -> str:
        if input.color_in_modal():
            reactive_color.set(input.color_in_modal())
        return f"Color 1: {input.my_color_1()}\nColor 2: {input.my_color_2()}\nColor in Modal: {input.color_in_modal()}"

    @reactive.effect
    @reactive.event(input.open_modal)
    async def _() -> None:
        ui.modal_show(ui.modal(color_input("color_in_modal", "Pick Color", value=reactive_color.get())))


app = App(app_ui, server)
