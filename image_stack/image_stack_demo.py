import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from rp import load_video, blend_images, as_rgb_image, as_byte_image
    import rp
    from image_stack import create_motion_blur_image
    import numpy as np
    return (
        as_byte_image,
        blend_images,
        create_motion_blur_image,
        load_video,
        mo,
        rp,
    )


@app.cell
def _(
    alphas_exponent_slider,
    as_byte_image,
    background_color_picker,
    blend_images,
    create_motion_blur_image,
    frame_size_slider,
    mo,
    num_frames_slider,
    rp,
    shadow_blur_slider,
    shadow_color_picker,
    shadow_opacity_slider,
    shadow_shift_slider,
    shift_x_slider,
    shift_y_slider,
    video,
    video_path_input,
    with_alpha_checkerboard,
):
    result = create_motion_blur_image(
        video,
        num_frames=num_frames_slider.value,
        total_shift_x=shift_x_slider.value,
        total_shift_y=shift_y_slider.value,
        frame_size=frame_size_slider.value,
        alphas_exponent=alphas_exponent_slider.value,
        shadow_shift=shadow_shift_slider.value,
        shadow_blur=shadow_blur_slider.value,
        shadow_opacity=shadow_opacity_slider.value,
        shadow_color=shadow_color_picker.value
    )

    final_result = blend_images(background_color_picker.value, result)
    if with_alpha_checkerboard.value:
        final_result = rp.with_alpha_checkerboard(final_result)
    final_result = as_byte_image(final_result, copy=False)

    mo.vstack([
        mo.md("# Image Stack Demo 📸"),
        video_path_input,
        mo.video(
            video_path_input.value,
            height=250,
            loop=True,
            autoplay=True,
            rounded=True,
            muted=True,
        ),
        mo.hstack([
            mo.vstack([
                mo.md("**Motion Controls**"),
                num_frames_slider,
                shift_x_slider,
                shift_y_slider,
                frame_size_slider,
                alphas_exponent_slider,
            ]),
            mo.vstack([
                mo.md("**Shadow Controls**"),
                shadow_shift_slider,
                shadow_blur_slider,
                shadow_opacity_slider,
                shadow_color_picker,
            ]),
            mo.vstack([
                mo.md("**Display Controls**"),
                background_color_picker,
                with_alpha_checkerboard,
            ]),
        ]),
        mo.md(f"""
        **Parameters**: 
        - Frames: {num_frames_slider.value}
        - Shift: {shift_x_slider.value}x, {shift_y_slider.value}y pixels  
        - Size: {frame_size_slider.value}×{frame_size_slider.value}px
        - Alpha curve: {alphas_exponent_slider.value}
        - Shadow: {shadow_shift_slider.value}px offset, {shadow_blur_slider.value}px blur, {shadow_opacity_slider.value} opacity
        """),
    ])
    return (final_result,)


@app.cell
def _(final_result, mo):
    mo.image(src=final_result)
    return


@app.cell
def _(mo):
    video_path_input = mo.ui.text(
        value="/Users/ryan/Downloads/StillPepper.mp4", 
        label="Video Path:",
        full_width=True
    )
    return (video_path_input,)


@app.cell
def _(load_video, video_path_input):
    video = load_video(video_path_input.value, use_cache=True)
    return (video,)


@app.cell
def _(mo, video):
    num_frames_slider = mo.ui.slider(
        start=3, stop=min(25, len(video)), value=10, step=1, 
        label="Frames:", include_input=True
    )

    shift_x_slider = mo.ui.slider(
        start=0, stop=500, value=200, step=10, 
        label="Shift X:", include_input=True
    )

    shift_y_slider = mo.ui.slider(
        start=0, stop=500, value=200, step=10, 
        label="Shift Y:", include_input=True
    )

    frame_size_slider = mo.ui.slider(
        start=128, stop=512, value=256, step=16, 
        label="Frame size:", include_input=True
    )

    alphas_exponent_slider = mo.ui.slider(
        start=0.1, stop=2.0, value=0.5, step=0.1, 
        label="Alpha exponent:", include_input=True
    )

    return (
        alphas_exponent_slider,
        frame_size_slider,
        num_frames_slider,
        shift_x_slider,
        shift_y_slider,
    )


@app.cell
def _(mo):
    shadow_shift_slider = mo.ui.slider(
        start=0, stop=50, value=10, step=1, 
        label="Shadow offset:", include_input=True
    )

    shadow_blur_slider = mo.ui.slider(
        start=0, stop=100, value=30, step=5, 
        label="Shadow blur:", include_input=True
    )

    shadow_opacity_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.25, step=0.05, 
        label="Shadow opacity:", include_input=True
    )

    return shadow_blur_slider, shadow_opacity_slider, shadow_shift_slider


@app.cell
def _(mo):
    with_alpha_checkerboard = mo.ui.switch(value=False,label='Alpha Checkerboard')
    return (with_alpha_checkerboard,)


@app.cell
def _(mo):
    shadow_color_picker = mo.ui.text(
        value="#000000",
        label="Shadow color:"
    )

    background_color_picker = mo.ui.text(
        value="#0000FF",
        label="Background color:"
    )

    return background_color_picker, shadow_color_picker


if __name__ == "__main__":
    app.run()
