import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from labeled_circle import labeled_circle
    import numpy as np
    return labeled_circle, mo


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _(
    diameter_slider,
    fill_color_picker,
    font_dropdown,
    mo,
    padding_slider,
    rim_color_picker,
    rim_width_slider,
    text_color_picker,
    text_input,
):
    fill_color = fill_color_picker.value
    rim_color = rim_color_picker.value
    text_color = text_color_picker.value

    mo.vstack([
        mo.md("# Labeled Circle Demo ⭕"),
        text_input,
        diameter_slider,
        padding_slider,
        rim_width_slider,
        fill_color_picker,
        rim_color_picker,
        text_color_picker,
        font_dropdown,
        mo.md(f"""
        **Parameters**: 
        - Text: "{text_input.value}"
        - Size: {diameter_slider.value}px diameter, {padding_slider.value}px padding
        - Rim: {rim_width_slider.value}px width
        - Font: {font_dropdown.value}
        """)
    ])
    return fill_color, rim_color, text_color


@app.cell
def _(
    diameter_slider,
    fill_color,
    font_dropdown,
    labeled_circle,
    mo,
    padding_slider,
    rim_color,
    rim_width_slider,
    text_color,
    text_input,
):
    result = labeled_circle(
        text=text_input.value,
        color=fill_color,
        rim_color=rim_color,
        rim_width=rim_width_slider.value,
        diameter=diameter_slider.value,
        padding=padding_slider.value,
        font=font_dropdown.value,
        text_color=text_color
    )

    mo.image(src=result, width=400)
    return


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

    rim_width_slider = mo.ui.slider(
        start=-50, stop=50, value=-20, step=2, 
        label="Rim width:", include_input=True
    )

    return diameter_slider, padding_slider, rim_width_slider, text_input


@app.cell
def _(mo):
    fill_color_picker = mo.ui.text(
        value="#FF00FF",
        label="Fill color:"
    )

    rim_color_picker = mo.ui.text(
        value="#FF00FF",
        label="Rim color:"
    )

    text_color_picker = mo.ui.text(
        value="#000000",
        label="Text color:"
    )

    font_dropdown = mo.ui.dropdown(
        options=["Futura", "Arial", "Helvetica", "Times", "Courier"],
        value="Futura",
        label="Font:"
    )

    return (
        fill_color_picker,
        font_dropdown,
        rim_color_picker,
        text_color_picker,
    )


if __name__ == "__main__":
    app.run()
