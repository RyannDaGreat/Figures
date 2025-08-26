import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from rp import load_video
    from film_strip import film_strip
    import numpy as np
    return film_strip, load_video, mo


@app.cell
def _(
    film_strip,
    height_slider,
    length_slider,
    mo,
    video,
    video_path_input,
    width_slider,
):
    result = film_strip(
        video,
        length=length_slider.value,
        height=height_slider.value,
        width=width_slider.value,
    )

    mo.vstack(
        [
            mo.md("# Film Strip Demo 🎬"),
            video_path_input,
            mo.image(src=result, width=800),
            length_slider,
            height_slider,
            width_slider,
            mo.md(
                f"**Parameters**: {length_slider.value} frames, {height_slider.value}×{width_slider.value} pixels"
            ),
            mo.video(
                video_path_input.value,
                height=250,
                loop=True,
                autoplay=True,
                rounded=True,
                muted=True,
            ),
        ]
    )
    return


@app.cell
def _(mo, video):
    length_slider = mo.ui.slider(
        start=1, stop=min(20, len(video)), value=4, step=1, label="Frames:",include_input=True,
    )
    height_slider = mo.ui.slider(
        start=240, stop=720, value=480, step=24, label="Frame height:",include_input=True,
    )
    width_slider = mo.ui.slider(
        start=320, stop=1080, value=720, step=40, label="Frame width:",include_input=True,
    )
    return height_slider, length_slider, width_slider


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


if __name__ == "__main__":
    app.run()
