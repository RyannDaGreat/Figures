import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from labeled_circle import labeled_circle
    import rp
    return labeled_circle, mo


@app.cell
def _(
    checkerboard_switch,
    crop_zeros_switch,
    diameter_slider,
    fill_color_picker,
    font_dropdown,
    font_size_slider,
    mo,
    padding_slider,
    rim_color_picker,
    rim_width_slider,
    text_color_picker,
    text_input,
    text_style_input,
):
    mo.vstack([
        mo.md("# Labeled Circle Demo ⭕"),
        text_input,
        mo.hstack([
            mo.vstack([
                mo.md("**Size Controls**"),
                diameter_slider,
                padding_slider,
                font_size_slider,
                rim_width_slider,
            ]),
            mo.vstack([
                mo.md("**Style Controls**"),
                font_dropdown,
                text_style_input,
                text_color_picker,
                checkerboard_switch,
                crop_zeros_switch,
            ]),
            mo.vstack([
                mo.md("**Color Controls**"),
                fill_color_picker,
                rim_color_picker,
            ]),
        ]),
        mo.md(f"""
        **Parameters**: 
        - Text: "{text_input.value}"
        - Size: {diameter_slider.value}px diameter, {font_size_slider.value}px font, {padding_slider.value}px padding
        - Rim: {rim_width_slider.value}px width
        - Font: {font_dropdown.value}
        - Style: {text_style_input.value}
        - Checkerboard: {"On" if checkerboard_switch.value else "Off"}
        - Crop Zeros: {"On" if crop_zeros_switch.value else "Off"}
        """)
    ])
    return


@app.cell
def _(
    checkerboard_switch,
    crop_zeros_switch,
    diameter_slider,
    fill_color_picker,
    font_dropdown,
    font_size_slider,
    labeled_circle,
    padding_slider,
    rim_color_picker,
    rim_width_slider,
    text_color_picker,
    text_input,
    text_style_input,
):
    fill_color = fill_color_picker.value
    rim_color = rim_color_picker.value

    result = labeled_circle(
        text=text_input.value,
        color=fill_color,
        rim_color=rim_color,
        rim_width=rim_width_slider.value,
        diameter=diameter_slider.value,
        padding=padding_slider.value,
        font=font_dropdown.value,
        text_color=text_color_picker.value,
        font_size=font_size_slider.value,
        text_style=text_style_input.value,
        with_checkerboard=checkerboard_switch.value,
        crop_zeros=crop_zeros_switch.value
    )

    return (result,)


@app.cell
def _(mo, result):
    mo.hstack([mo.image(src=result)],align='center')
    return


@app.cell
def _(mo):
    crop_zeros_switch = mo.ui.switch(
        value=False, 
        label='Crop Zeros'
    )

    return (crop_zeros_switch,)


@app.cell
def _(mo):
    text_input = mo.ui.text(
        value="42", 
        label="Text content:",
        full_width=True
    )

    diameter_slider = mo.ui.slider(
        start=100, stop=500, value=257, step=10, 
        label="Diameter:", include_input=True
    )

    padding_slider = mo.ui.slider(
        start=0, stop=50, value=10, step=2, 
        label="Padding:", include_input=True
    )

    font_size_slider = mo.ui.slider(
        start=10, stop=300, value=167, step=5, 
        label="Font size:", include_input=True
    )

    rim_width_slider = mo.ui.slider(
        start=-50, stop=50, value=-20, step=2, 
        label="Rim width:", include_input=True
    )

    return (
        diameter_slider,
        font_size_slider,
        padding_slider,
        rim_width_slider,
        text_input,
    )


@app.cell
def _(mo):
    font_dropdown = mo.ui.dropdown(
        options=["Futura", "Arial", "Helvetica", "Times", "Courier"],
        value="Futura",
        label="Font:"
    )

    text_style_input = mo.ui.text(
        value="bold",
        label="Text style:"
    )

    checkerboard_switch = mo.ui.switch(
        value=True, 
        label='Alpha Checkerboard'
    )

    return checkerboard_switch, font_dropdown, text_style_input


@app.cell
def _(mo):
    fill_color_picker = mo.ui.text(
        value="#00FF00",  # Green instead of magenta
        label="Fill color:"
    )

    rim_color_picker = mo.ui.text(
        value="#FF0000",  # Red instead of magenta
        label="Rim color:"
    )

    text_color_picker = mo.ui.text(
        value="#000000",
        label="Text color:"
    )

    return fill_color_picker, rim_color_picker, text_color_picker


if __name__ == "__main__":
    app.run()
