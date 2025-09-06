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
    return fullvid, mo, rp, tween


@app.cell
def _(mo):
    mo.md("""# Full Video Visualization Demo 🎬""")
    return


@app.cell
def _(fullvid, mo):
    # Import all the data and functions from fullvid

    # Get the current data from fullvid module
    target_video = fullvid.target_video
    counter_video = fullvid.counter_video
    target_tracks = fullvid.target_tracks
    counter_tracks = fullvid.counter_tracks
    target_visibles = fullvid.target_visibles
    counter_visibles = fullvid.counter_visibles
    N, T, H, W = fullvid.N, fullvid.T, fullvid.H, fullvid.W
    colors = fullvid.colors
    circles = fullvid.circles

    # Import functions
    circles_layer = fullvid.circles_layer
    trails_layer = fullvid.trails_layer
    arrows_layer = fullvid.arrows_layer
    srgb_blend = fullvid.srgb_blend
    blended_video_layer = fullvid.blended_video_layer
    final_frame = fullvid.final_frame

    mo.md(f"**Data loaded**: {T} frames, {N} tracks, {H}x{W} resolution")
    return N, T, final_frame


@app.cell
def _(final_frame, mo, sliders, track_checkboxes):
    # Get selected track indices from checkboxes
    selected_tracks = [
        i for i, checkbox in enumerate(track_checkboxes) if checkbox.value
    ]
    track_numbers = selected_tracks if selected_tracks else None

    result = final_frame(
        frame_number=sliders.value["frame_number"],
        video_alpha=sliders.value["video_alpha"],
        track_alpha=sliders.value["track_alpha"],
        circles_alpha=sliders.value["circles_alpha"],
        arrows_alpha=sliders.value["arrows_alpha"],
        target_trails_alpha=sliders.value["target_trails_alpha"],
        counter_trails_alpha=sliders.value["counter_trails_alpha"],
        blended_trails_alpha=sliders.value["blended_trails_alpha"],
        track_numbers=track_numbers,
    )

    mo.vstack(
        [
            mo.vstack(
                [
                    sliders["frame_number"],
                    sliders["video_alpha"],
                    sliders["track_alpha"],
                    sliders["circles_alpha"],
                    sliders["arrows_alpha"],
                    sliders["target_trails_alpha"],
                    sliders["counter_trails_alpha"],
                    sliders["blended_trails_alpha"],
                    mo.md("**Track Selection:**"),
                    mo.hstack(track_checkboxes),
                ]
            ),
            mo.md(
                f"""
        **final_frame({sliders.value["frame_number"]}, {sliders.value["video_alpha"]:.2f}, {sliders.value["track_alpha"]:.2f}, {sliders.value["circles_alpha"]:.2f}, {sliders.value["arrows_alpha"]:.2f}, {sliders.value["target_trails_alpha"]:.2f}, {sliders.value["counter_trails_alpha"]:.2f}, {sliders.value["blended_trails_alpha"]:.2f})**
        """
            ),
        ]
    )
    return


@app.cell
def _(N, T, mo):
    # All sliders in a single dictionary for easier management
    sliders = mo.ui.dictionary(
        {
            "frame_number": mo.ui.slider(
                start=0,
                stop=T - 1,
                value=T // 2,
                step=1,
                label="frame_number:",
                include_input=True,
            ),
            "video_alpha": mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=0.5,
                step=0.01,
                label="video_alpha:",
                include_input=True,
            ),
            "track_alpha": mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=0.5,
                step=0.01,
                label="track_alpha:",
                include_input=True,
            ),
            "circles_alpha": mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=1.0,
                step=0.01,
                label="circles_alpha:",
                include_input=True,
            ),
            "arrows_alpha": mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=1.0,
                step=0.01,
                label="arrows_alpha:",
                include_input=True,
            ),
            "target_trails_alpha": mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=0.8,
                step=0.01,
                label="target_trails_alpha:",
                include_input=True,
            ),
            "counter_trails_alpha": mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=0.8,
                step=0.01,
                label="counter_trails_alpha:",
                include_input=True,
            ),
            "blended_trails_alpha": mo.ui.slider(
                start=0.0,
                stop=1.0,
                value=0.6,
                step=0.01,
                label="blended_trails_alpha:",
                include_input=True,
            ),
        }
    )
    # Track selection checkboxes - one for each track
    track_checkboxes = [
        mo.ui.checkbox(value=True, label=str(i + 1)) for i in range(N)
    ]
    return sliders, track_checkboxes


@app.cell
def _(T, final_frame, rp, tween):
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


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
