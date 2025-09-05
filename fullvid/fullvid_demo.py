import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import rp
    import fullvid
    import numpy as np
    return fullvid, mo, np, rp


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
def _(mo, result):
    mo.image(src=result, width=720)
    return


@app.cell
def _(
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
    return result, track_numbers


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


@app.cell
def _(np, rp):
    def demo_tween():
        #Just shows how to make a basic animation with tweening
    
        def tween_segment(start, stop, num):
            return np.linspace(stop, start, num, endpoint=False)[::-1]
    
        state = {
            'x':3,
            'y':5,
        }
        timeline = [state]
    
        def tween_to(duration, **end_states):
            #To wait, just dont pass any kwargs...
            assert set(end_states)<=set(timeline[0]), 'Tween cannot add new elements to state'
    
            start_state = timeline[-1]
    
            tweens = {
                name: tween_segment(start_state[name], end_states[name], duration)
                for name in end_states
            }
            deltas = rp.dict_list_transpose(tweens)
    
            for delta in deltas:
                new_state = {**start_state} | delta
                timeline.append(new_state)
    
        def render_state(state):
            image = rp.uniform_byte_color_image(500,500,'dark blue')
            x, y = rp.destructure(state)
            image = rp.cv_draw_circle(image,x,y,copy=False,radius=20,rim=3)
            image = rp.labeled_image(image,f'x={x:.02f}, y={y:.02f}',size=30,font='Futura')
            return image
        
        def render_video():
            video = (render_state(state) for state in timeline)
            video = rp.IteratorWithLen(video, len(timeline))
            return video
    
        tween_to(3,x=10,y=10)
        tween_to(30,x=0,y=400)
        tween_to(30,x=250,y=400)
        tween_to(30,x=500,y=500)
        tween_to(30,x=0)
        tween_to(30,x=500)
    
        return rp.display_video(list(rp.eta(render_video())),loop=True)
    demo_tween()
    return


@app.cell
def _(
    arrows_alpha_slider,
    blended_trails_alpha_slider,
    circles_alpha_slider,
    counter_trails_alpha_slider,
    final_frame,
    np,
    rp,
    target_trails_alpha_slider,
    track_alpha_slider,
    track_numbers,
    video_alpha_slider,
):
    def tween_segment(start, stop, num:int):
        return np.linspace(stop, start, num, endpoint=False)[::-1]

    def tween_to(duration:int, end_states:dict):
        #To wait, just dont pass any kwargs...
        assert set(end_states)<=set(timeline[0]), 'Tween cannot add new elements to state'

        start_state = timeline[-1]

        tweens = {
            name: tween_segment(start_state[name], end_states[name], duration)
            for name in end_states
        }
        deltas = rp.dict_list_transpose(tweens)

        for delta in deltas:
            new_state = {**start_state} | delta
            timeline.append(new_state)

    def render_state(state):
        image = rp.uniform_byte_color_image(500,500,'dark blue')
        x,y=rp.destructure(state)
        image = rp.cv_draw_circle(image,x,y,copy=False,radius=20,rim=3)
        image = rp.labeled_image(image,f'x={x:.02f}, y={y:.02f}',size=30,font='Futura')
        return image
    
    def render_video():
        video = (final_frame(**state) for state in timeline)
        video = rp.IteratorWithLen(video, len(timeline))
        return video

    initial_state = dict(
        frame_number=0,
        video_alpha=video_alpha_slider.value,
        track_alpha=track_alpha_slider.value,
        circles_alpha=circles_alpha_slider.value,
        arrows_alpha=arrows_alpha_slider.value,
        target_trails_alpha=target_trails_alpha_slider.value,
        counter_trails_alpha=counter_trails_alpha_slider.value,
        blended_trails_alpha=blended_trails_alpha_slider.value,
        track_numbers=track_numbers,
    )

    timeline = [
        initial_state
    ]

    timeline_states = [
        dict(
        frame_number=0,
        video_alpha=video_alpha_slider.value,
        track_alpha=track_alpha_slider.value,
        circles_alpha=circles_alpha_slider.value,
        arrows_alpha=arrows_alpha_slider.value,
        target_trails_alpha=target_trails_alpha_slider.value,
        counter_trails_alpha=counter_trails_alpha_slider.value,
        blended_trails_alpha=blended_trails_alpha_slider.value,
        track_numbers=track_numbers,
    ),
            dict(
        frame_number=0,
        video_alpha=video_alpha_slider.value,
        track_alpha=track_alpha_slider.value,
        circles_alpha=circles_alpha_slider.value,
        arrows_alpha=arrows_alpha_slider.value,
        target_trails_alpha=target_trails_alpha_slider.value,
        counter_trails_alpha=counter_trails_alpha_slider.value,
        blended_trails_alpha=blended_trails_alpha_slider.value,
        track_numbers=track_numbers,
    ),
            dict(
        frame_number=0,
        video_alpha=video_alpha_slider.value,
        track_alpha=track_alpha_slider.value,
        circles_alpha=circles_alpha_slider.value,
        arrows_alpha=arrows_alpha_slider.value,
        target_trails_alpha=target_trails_alpha_slider.value,
        counter_trails_alpha=counter_trails_alpha_slider.value,
        blended_trails_alpha=blended_trails_alpha_slider.value,
        track_numbers=track_numbers,
    ),
    ]


    for state in timeline_states:
        tween_to(30, state)
    
    rp.display_video(list(rp.eta(render_video(),'Rendering')),loop=True)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
