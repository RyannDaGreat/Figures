import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""# Full Video Visualization Demo 🎬""")
    return


@app.cell
def _(mo):
    # Import all the data and functions from fullvid
    import fullvid

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
def _(
    T,
    arrows_alpha_slider,
    blended_trails_alpha_slider,
    circles_alpha_slider,
    counter_trails_alpha_slider,
    final_frame,
    frame_number_slider,
    mo,
    target_trails_alpha_slider,
    track_alpha_slider,
    track_checkboxes,
    video_alpha_slider,
):
    # Get selected track indices from checkboxes
    selected_tracks = [i for i, checkbox in enumerate(track_checkboxes) if checkbox.value]
    track_numbers = selected_tracks if selected_tracks else None
    
    result = final_frame(
        frame_number=frame_number_slider.value,
        video_alpha=video_alpha_slider.value,
        track_alpha=track_alpha_slider.value,
        circles_alpha=circles_alpha_slider.value,
        arrows_alpha=arrows_alpha_slider.value,
        target_trails_alpha=target_trails_alpha_slider.value,
        counter_trails_alpha=counter_trails_alpha_slider.value,
        blended_trails_alpha=blended_trails_alpha_slider.value,
        track_numbers=track_numbers,
    )

    mo.vstack([
        mo.image(src=result, width=720),
        mo.vstack([
            frame_number_slider,
            video_alpha_slider, 
            track_alpha_slider,
            circles_alpha_slider,
            arrows_alpha_slider,
            target_trails_alpha_slider,
            counter_trails_alpha_slider,
            blended_trails_alpha_slider,
            mo.md("**Track Selection:**"),
            mo.hstack(track_checkboxes),
        ]),
        mo.md(f"""
        **final_frame({frame_number_slider.value}, {video_alpha_slider.value:.2f}, {track_alpha_slider.value:.2f}, {circles_alpha_slider.value:.2f}, {arrows_alpha_slider.value:.2f}, {target_trails_alpha_slider.value:.2f}, {counter_trails_alpha_slider.value:.2f}, {blended_trails_alpha_slider.value:.2f})**
        """)
    ])
    return


@app.cell
def _(T, mo):
    # Frame number control
    frame_number_slider = mo.ui.slider(
        start=0, stop=T-1, value=T//2, step=1,
        label="frame_number:", include_input=True
    )
    return (frame_number_slider,)


@app.cell
def _(mo):
    # Video alpha control - blends between target and counter videos
    video_alpha_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.5, step=0.01,
        label="video_alpha:", include_input=True
    )
    return (video_alpha_slider,)


@app.cell 
def _(mo):
    # Track alpha control - blends between target and counter track positions
    track_alpha_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.5, step=0.01,
        label="track_alpha:", include_input=True
    )
    return (track_alpha_slider,)


@app.cell
def _(mo):
    # Circles alpha control - opacity of circles layer
    circles_alpha_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=1.0, step=0.01,
        label="circles_alpha:", include_input=True
    )
    return (circles_alpha_slider,)


@app.cell
def _(mo):
    # Arrows alpha control - opacity of arrows layer
    arrows_alpha_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=1.0, step=0.01,
        label="arrows_alpha:", include_input=True
    )
    return (arrows_alpha_slider,)


@app.cell
def _(mo):
    # Target trails alpha control - opacity of target trails layer
    target_trails_alpha_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.8, step=0.01,
        label="target_trails_alpha:", include_input=True
    )
    return (target_trails_alpha_slider,)


@app.cell
def _(mo):
    # Counter trails alpha control - opacity of counter trails layer
    counter_trails_alpha_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.8, step=0.01,
        label="counter_trails_alpha:", include_input=True
    )
    return (counter_trails_alpha_slider,)


@app.cell
def _(mo):
    # Blended trails alpha control - opacity of blended trails layer
    blended_trails_alpha_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.6, step=0.01,
        label="blended_trails_alpha:", include_input=True
    )
    return (blended_trails_alpha_slider,)


@app.cell
def _(N, mo):
    # Track selection checkboxes - one for each track
    track_checkboxes = [
        mo.ui.checkbox(value=True, label=str(i+1))
        for i in range(N)
    ]
    return (track_checkboxes,)




if __name__ == "__main__":
    app.run()
