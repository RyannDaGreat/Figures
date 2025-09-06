import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import rp
    import fullvid
    import numpy as np
    from rp.libs.tweenline import tween

    from fullvid import (
        target_video,
        counter_video,
        target_tracks,
        counter_tracks,
        target_visibles,
        counter_visibles,
        N,
        T,
        H,
        W,
        colors,
        circles,
        circles_layer,
        trails_layer,
        arrows_layer,
        srgb_blend,
        blended_video_layer,
        final_frame,
    )
    return N, T, final_frame, mo, rp, tween


@app.cell
def _(mo, result):
    mo.image(result)
    return


@app.cell
def _(final_frame, mo, sliders, track_checkboxes):
    # Get selected track indices from checkboxes
    selected_tracks = [i for i, checkbox in enumerate(track_checkboxes) if checkbox.value]
    track_numbers = selected_tracks if selected_tracks else None

    result = final_frame(
        **{arg_name: slider.value for arg_name, slider in sliders.items()},
        track_numbers=track_numbers,
    )

    mo.vstack(
        [
            mo.vstack(
                [
                    *sliders.values(),
                    mo.md("**Track Selection:**"),
                    mo.hstack(track_checkboxes),
                ]
            ),
        ]
    )
    return (result,)


@app.cell
def _(N, T, mo):
    #Marimo Preview Controls
    sliders = mo.ui.dictionary(
        {
            "frame_number": mo.ui.slider(
                start=0,
                stop=T - 1,
                value=T // 2,
                step=1,
                label="frame_number:",
                include_input=True,
            )
        }
        | {
            arg_name: mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=0.5,
                step=0.01,
                label=arg_name,
                include_input=True,
            )
            for arg_name in [
                "video_alpha",
                "track_alpha",
                "circles_alpha",
                "arrows_alpha",
                "target_trails_alpha",
                "counter_trails_alpha",
                "blended_trails_alpha",
            ]
        }
    )
    track_checkboxes = [
        mo.ui.checkbox(value=True, label=str(i + 1)) for i in range(N)
    ]
    return sliders, track_checkboxes


@app.cell
def _(T, final_frame, rp, tween):
    #Animation Definition
    timeline = (
        dict(
            frame_number=0,
            video_alpha=0.0,
            track_alpha=0.0,
            circles_alpha=0.0,
            arrows_alpha=1.0,
            target_trails_alpha=0.0,
            counter_trails_alpha=0.0,
            blended_trails_alpha=0.0,
            track_numbers=[],
        )
        >> tween(T - 1, frame_number=T - 1)
        >> tween(frame_number=0, track_numbers=[0, 1, 2])
        >> tween(T - 1, frame_number=T - 1) + tween(T - 1, circles_alpha=1)
    )


    def get_frame(frame_number):
        state = timeline[frame_number]
        frame = final_frame(**state)
        return frame


    def get_video():
        for state in rp.eta(timeline, "Rendering"):
            frame = final_frame(**state)
            yield frame


    # # rp.display_video(get_video())
    # rp.display_video(get_video())
    return get_frame, get_video, timeline


@app.cell
def _(get_frame, mo, preview_frame_slider, render_video_button):
    mo.vstack(
        [
            mo.image(get_frame(preview_frame_slider.value), width=720),
            preview_frame_slider,
            render_video_button,
        ],
    )
    return


@app.cell
def _(mo, timeline):
    preview_frame_slider = mo.ui.slider(
        start=0,
        stop=len(timeline) - 1,
        value=0,
        step=1,
        label="Frame Number:",
        include_input=True,
        debounce=False,
        full_width=True,
    )

    render_video_button = mo.ui.run_button(label="Render Video")
    return preview_frame_slider, render_video_button


@app.cell
def _(get_video, render_video_button, rp):
    video = None
    if render_video_button.value:
        video = rp.display_video(get_video())
    video
    return


if __name__ == "__main__":
    app.run()
