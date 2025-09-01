import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from arrow import skia_draw_arrow
    import rp
    import numpy as np
    return mo, rp, skia_draw_arrow


@app.cell
def _(
    end_width_slider,
    fill_switch,
    fill_color_picker,
    mo,
    shadow_blur_slider,
    shadow_color_picker,
    shadow_dx_slider,
    shadow_dy_slider,
    shadow_opacity_slider,
    shadow_switch,
    start_width_slider,
    stroke_dash_scale_slider,
    stroke_phase_slider,
    stroke_cap_dropdown,
    stroke_color_picker,
    stroke_join_dropdown,
    stroke_miter_limit_slider,
    stroke_switch,
    stroke_type_dropdown,
    stroke_width_slider,
    tip_dimple_slider,
    tip_height_slider,
    tip_width_slider,
    x0_slider,
    x1_slider,
    y0_slider,
    y1_slider,
):
    mo.vstack([
        mo.md("# Arrow Demo 🏹"),
        mo.hstack([
            mo.vstack([
                mo.md("**Arrow Position**"),
                x0_slider,
                y0_slider,
                x1_slider,
                y1_slider,
            ]),
            mo.vstack([
                mo.md("**Arrow Shape**"),
                tip_width_slider,
                tip_height_slider,
                tip_dimple_slider,
                start_width_slider,
                end_width_slider,
            ]),
            mo.vstack([
                mo.md("**Stroke Style**"),
                stroke_switch,
                stroke_width_slider,
                stroke_type_dropdown,
                stroke_cap_dropdown,
                stroke_join_dropdown,
                stroke_miter_limit_slider,
                stroke_dash_scale_slider,
                stroke_phase_slider,
            ]),
            mo.vstack([
                mo.md("**Colors & Effects**"),
                fill_switch,
                fill_color_picker,
                stroke_color_picker,
                shadow_switch,
                shadow_color_picker,
                shadow_dx_slider,
                shadow_dy_slider,
                shadow_blur_slider,
                shadow_opacity_slider,
            ]),
        ]),
        mo.md(f"""
        **Arrow Parameters**: 
        - Start: ({x0_slider.value}, {y0_slider.value})
        - End: ({x1_slider.value}, {y1_slider.value})
        - Tip: {tip_width_slider.value}px width, {tip_height_slider.value}px height, {tip_dimple_slider.value}px dimple
        - Shaft: {start_width_slider.value}px start width, {end_width_slider.value}px end width
        - Stroke: {stroke_width_slider.value}px {stroke_type_dropdown.value}, {stroke_cap_dropdown.value} caps, {stroke_join_dropdown.value} joins
        - Fill: {"On" if fill_switch.value else "Off"} ({fill_color_picker.value}), Stroke: {"On" if stroke_switch.value else "Off"} ({stroke_color_picker.value})
        - Shadow: {"On" if shadow_switch.value else "Off"} at ({shadow_dx_slider.value}, {shadow_dy_slider.value}) color={shadow_color_picker.value} blur={shadow_blur_slider.value}px opacity={shadow_opacity_slider.value}
        """)
    ])
    return


@app.cell
def _(
    end_width_slider,
    fill_switch,
    fill_color_picker,
    rp,
    shadow_blur_slider,
    shadow_color_picker,
    shadow_dx_slider,
    shadow_dy_slider,
    shadow_opacity_slider,
    shadow_switch,
    skia_draw_arrow,
    start_width_slider,
    stroke_dash_scale_slider,
    stroke_phase_slider,
    stroke_cap_dropdown,
    stroke_color_picker,
    stroke_join_dropdown,
    stroke_miter_limit_slider,
    stroke_switch,
    stroke_type_dropdown,
    stroke_width_slider,
    tip_dimple_slider,
    tip_height_slider,
    tip_width_slider,
    x0_slider,
    x1_slider,
    y0_slider,
    y1_slider,
):
    # Create a blank canvas
    canvas_width, canvas_height = 600, 400
    canvas = rp.as_rgba_image(rp.uniform_float_color_image(canvas_height, canvas_width), copy=False)

    # Draw the arrow
    result = skia_draw_arrow(
        canvas,
        x0=x0_slider.value,
        y0=y0_slider.value,
        x1=x1_slider.value,
        y1=y1_slider.value,
        tip_width=tip_width_slider.value,
        tip_height=tip_height_slider.value,
        tip_dimple=tip_dimple_slider.value,
        end_width=end_width_slider.value,
        start_width=start_width_slider.value,
        fill=fill_color_picker.value if fill_switch.value else None,
        stroke=stroke_switch.value,
        stroke_color=stroke_color_picker.value,
        stroke_width=stroke_width_slider.value,
        stroke_type=stroke_type_dropdown.value,
        stroke_cap=stroke_cap_dropdown.value,
        stroke_join=stroke_join_dropdown.value,
        stroke_miter_limit=stroke_miter_limit_slider.value,
        stroke_dash_scale=stroke_dash_scale_slider.value,
        stroke_phase=stroke_phase_slider.value,
        shadow=shadow_switch.value,
        shadow_blur=shadow_blur_slider.value,
        shadow_dx=shadow_dx_slider.value,
        shadow_dy=shadow_dy_slider.value,
        shadow_color=shadow_color_picker.value,
        shadow_opacity=shadow_opacity_slider.value
    )

    return (result,)


@app.cell
def _(mo, result):
    mo.hstack([mo.image(src=result)], align='center')
    return


@app.cell
def _(mo):
    # Arrow position controls
    x0_slider = mo.ui.slider(
        start=50, stop=550, value=100, step=10,
        label="Start X:", include_input=True
    )

    y0_slider = mo.ui.slider(
        start=50, stop=350, value=200, step=10,
        label="Start Y:", include_input=True
    )

    x1_slider = mo.ui.slider(
        start=50, stop=550, value=500, step=10,
        label="End X:", include_input=True
    )

    y1_slider = mo.ui.slider(
        start=50, stop=350, value=200, step=10,
        label="End Y:", include_input=True
    )

    return x0_slider, x1_slider, y0_slider, y1_slider


@app.cell
def _(mo):
    # Arrow shape controls
    tip_width_slider = mo.ui.slider(
        start=-100, stop=100, value=15, step=1,
        label="Tip Width:", include_input=True
    )

    tip_height_slider = mo.ui.slider(
        start=-100, stop=100, value=15, step=1,
        label="Tip Height:", include_input=True
    )

    tip_dimple_slider = mo.ui.slider(
        start=-50, stop=50, value=5, step=1,
        label="Tip Dimple:", include_input=True
    )
    
    end_width_slider = mo.ui.slider(
        start=0, stop=50, value=5, step=1,
        label="End Width:", include_input=True
    )
    
    start_width_slider = mo.ui.slider(
        start=0, stop=50, value=3, step=1,
        label="Start Width:", include_input=True
    )

    return end_width_slider, start_width_slider, tip_dimple_slider, tip_height_slider, tip_width_slider


@app.cell
def _(mo):
    # Stroke style controls
    stroke_width_slider = mo.ui.slider(
        start=1, stop=20, value=3, step=1,
        label="Stroke Width:", include_input=True
    )

    stroke_type_dropdown = mo.ui.dropdown(
        options=["solid", "dashed", "dotted", "dashdot", "dashdotdot"],
        value="solid",
        label="Stroke Type:"
    )

    stroke_cap_dropdown = mo.ui.dropdown(
        options=["round", "butt", "square"],
        value="round",
        label="Stroke Cap:"
    )

    stroke_join_dropdown = mo.ui.dropdown(
        options=["miter", "round", "bevel"],
        value="round",
        label="Stroke Join:"
    )
    
    stroke_switch = mo.ui.switch(
        value=True, 
        label='Stroke'
    )
    
    stroke_miter_limit_slider = mo.ui.slider(
        start=1, stop=20, value=10, step=0.5,
        label="Miter Limit:", include_input=True
    )
    
    stroke_dash_scale_slider = mo.ui.slider(
        start=0.1, stop=3.0, value=1.0, step=0.1,
        label="Dash Scale:", include_input=True
    )
    
    stroke_phase_slider = mo.ui.slider(
        start=0, stop=100, value=0, step=1,
        label="Dash Phase:", include_input=True
    )

    return (
        stroke_cap_dropdown,
        stroke_join_dropdown,
        stroke_miter_limit_slider,
        stroke_type_dropdown,
        stroke_width_slider,
        stroke_switch,
        stroke_dash_scale_slider,
        stroke_phase_slider,
    )


@app.cell
def _(mo):
    # Color and effect controls
    fill_color_picker = mo.ui.text(
        value="#4A90E2",  # Nice blue
        label="Fill Color:"
    )

    stroke_color_picker = mo.ui.text(
        value="#2C3E50",  # Dark blue-gray
        label="Stroke Color:"
    )

    shadow_switch = mo.ui.switch(
        value=True, 
        label='Shadow'
    )

    shadow_blur_slider = mo.ui.slider(
        start=0, stop=20, value=5, step=1,
        label="Shadow Blur:", include_input=True
    )
    
    shadow_dx_slider = mo.ui.slider(
        start=-20, stop=20, value=3, step=1,
        label="Shadow X:", include_input=True
    )
    
    shadow_dy_slider = mo.ui.slider(
        start=-20, stop=20, value=3, step=1,
        label="Shadow Y:", include_input=True
    )
    
    shadow_opacity_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.5, step=0.05,
        label="Shadow Opacity:", include_input=True
    )
    
    fill_switch = mo.ui.switch(
        value=True, 
        label='Fill'
    )
    
    shadow_color_picker = mo.ui.text(
        value="#000000",  # Black shadow
        label="Shadow Color:"
    )

    return (
        fill_color_picker,
        fill_switch,
        shadow_blur_slider,
        shadow_color_picker,
        shadow_dx_slider,
        shadow_dy_slider,
        shadow_opacity_slider,
        shadow_switch,
        stroke_color_picker,
    )


if __name__ == "__main__":
    app.run()
