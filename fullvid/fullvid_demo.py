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
    from functools import partial

    from fullvid import final_frame, N, T, H, W
    return N, T, final_frame, mo, partial, rp, tween


@app.cell
def _(mo, result):
    mo.image(result)
    return


@app.cell
def _(controls, final_frame, mo, track_checkboxes):
    # Get selected track indices from checkboxes
    selected_tracks = [
        i for i, checkbox in enumerate(track_checkboxes) if checkbox.value
    ]
    track_numbers = selected_tracks if selected_tracks else None

    result = final_frame(
        **{arg_name: control.value for arg_name, control in controls.items()},
        track_numbers=track_numbers,
    )

    mo.vstack(
        [
            mo.vstack(
                [
                    *controls.values(),
                    mo.md("**Track Selection:**"),
                    mo.hstack(track_checkboxes),
                ]
            ),
        ]
    )
    return (result,)


@app.cell
def _(N, T, mo):
    # Marimo Preview Controls
    controls = mo.ui.dictionary(
        {
            arg_name: mo.ui.slider(
                start=min_val,
                stop=max_val,
                value=T // 2,
                step=1,
                label=arg_name,
                include_input=True,
            )
            for arg_name, (min_val, max_val) in dict(
                frame_number=[0, T - 1],
                status_width=[0, 500],
                status_offset=[0, 100],
            ).items()
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
                "status_alpha",
                "hand_alpha",
                "hand_size",
                "chat_alpha",
            ]
        }
        | {
            arg_name: mo.ui.text(
                value="blue",
                label=arg_name,
            )
            for arg_name in [
                "status_text",
                "status_color",
                "chat_text",
                "chat_background_color",
                "chat_rim_color", 
                "chat_text_color",
            ]
        }
        | {
            arg_name: mo.ui.checkbox(
                value=False,
                label=arg_name,
            )
            for arg_name in [
                "hand_grabbing",
            ]
        }
        | {
            arg_name: mo.ui.number(
                value=0,
                label=arg_name,
                step=1,
            )
            for arg_name in [
                "hand_dx",
                "hand_dy",
                "chat_width",
                "chat_height",
                "chat_font_size",
                "chat_y_offset",
                "status_x_shift",
            ]
        }
    )
    track_checkboxes = [
        mo.ui.checkbox(value=True, label=str(i + 1)) for i in range(N)
    ]
    return controls, track_checkboxes


@app.cell
def _(N, T, mo, partial, rp, tween):
    # Animation Definition

    timescale=4
    def stween(num_frames=1,**kwargs):
        return tween(round(num_frames*timescale),**kwargs)
    cstween = partial(stween, ease='cubic')
    ctween = partial(tween, ease='cubic')

    play_video_no_end = tween(T - 1, frame_number=T - 1)
    play_video = play_video_no_end >> tween(frame_number=0)
    boom_video = play_video_no_end >> tween(T - 1, frame_number=0) #Boomerang

    status_input_color  = rp.as_numpy_array(rp.as_rgba_float_color("dark green"  ))
    status_output_color = rp.as_numpy_array(rp.as_rgba_float_color("dark hotpink"))
    status_right_shift = 470
    status_right_width = 350
    status_left_width = 300
    status_right  = stween(20, status_x_shift = status_right_shift, status_width=status_right_width, ease='cubic')
    status_left   = stween(20, status_x_shift =                0  , status_width=status_left_width , ease='cubic')
    status_visi   = stween(20, status_alpha=1, status_offset=30, ease='cubic')

    #Change text half-way through a switch
    status_input_str = "Input Video" 
    status_output_str = "Edited Video"
    status_input_text  = stween(10) >> stween(10, status_text=status_input_str )
    status_output_text = stween(10) >> stween(10, status_text=status_output_str)

    status_input  = status_left  + status_input_text  + stween(20, status_color=status_input_color , video_alpha=0, ease='cubic') 
    status_output = status_right + status_output_text + stween(20, status_color=status_output_color, video_alpha=1, ease='cubic') 

    status_output_state = dict(status_color=status_output_color, video_alpha=1, status_x_shift = status_right_shift, status_width = status_right_width)

    chat_collapse = stween(20,  chat_width=  0)
    chat_fadeout = stween(20, chat_alpha = .0)
    chat_intro  = stween(20, chat_width=1000, chat_alpha =.75, chat_text = "Video Motion Edit")
    chat_step1  = stween(20, chat_width=1000, chat_alpha =.75, chat_text = "Step 1: Add Tracking Points")
    chat_step2  = stween(20, chat_width=1000, chat_alpha =.75, chat_text = "Step 2: Edit Trajectories")
    chat_manytraj  = stween(20, chat_width=1000, chat_alpha =.75, chat_text = "Edit Many Points")

    enable_counter_trails = stween(1, counter_trails_alpha=1)

    chosen_numbers = [3, 5]#basketball
    chosen_numbers = [0,1,2]#Swan

    reveal_tracks = (
           stween(track_numbers=chosen_numbers[:1])
        >> stween(5)
        >> stween(track_numbers=chosen_numbers[:2])
        >> stween(5)
        >> stween(track_numbers=chosen_numbers[:3])
    )

    default_frame_number = 394#Hack because the slider doesnt persist

    hands_fadein = stween(20, hand_alpha=1.0)

    timeline = (
        dict(
            frame_number=0,
            video_alpha=0.0,
            track_alpha=0.0,
            circles_alpha=1.0,
            arrows_alpha=1.0,
            target_trails_alpha=0.0,
            counter_trails_alpha=0.0,
            blended_trails_alpha=0.0,
            hand_grabbing=False,
            hand_alpha=0.0,
            hand_dx=-20,
            hand_dy=20,
            hand_size=1.0,
            status_width=0,
            status_offset=0.0, 
            status_alpha =0.0,
            status_text="Input Video",
            status_color=status_input_color,
            chat_alpha=1.0,
            chat_text="Step 1: Add Tracking Points",
            chat_background_color="black",
            chat_rim_color="gray",
            chat_text_color="white",
            chat_width=0,
            chat_height=120,
            chat_font_size=64,
            chat_y_offset=-20,
            track_numbers=[],
            status_x_shift=0,
        )
        >> play_video + status_visi + status_input
        >> play_video + chat_intro
        >> play_video + chat_fadeout + status_output
        >> play_video
        >> status_input + stween(chat_width=0)
        >> play_video + (
            chat_step1
            >> stween(10)
            >> reveal_tracks
        )
        >> play_video + chat_fadeout + enable_counter_trails
        >> play_video
        >> (stween(30, frame_number=timescale*30, ease='quad_out') >> stween(30, frame_number=0, ease='cubic')) + (
            stween(60)
            >> chat_step2
            >> stween(20, hand_dy=10, hand_dx=0, hand_size=1, hand_alpha=1.0, ease='cubic')
            >> stween(hand_grabbing=True)
        )
        >> stween(30, target_trails_alpha = 1., track_alpha = 1.)
        >> play_video * 2 + tween(T * 2, **status_output_state, ease='cubic') + 
        (tween(T) >> tween(T, status_text = status_output_str, counter_trails_alpha=0, arrows_alpha=0, hand_alpha=0, hand_size=.5, ease='cubic'))
        >> play_video * 2
        >> play_video + stween(20, circles_alpha = 0, target_trails_alpha=0, chat_alpha=0, ease='cubic')

        >> play_video + stween(track_alpha=0) + status_input + ( chat_manytraj >> stween(track_numbers = range(N)) >> stween(20, circles_alpha=1))
        >> play_video + ( stween(20) + cstween(20, counter_trails_alpha=1)) 


        >> cstween(hand_grabbing=False, hand_size=1, arrows_alpha=1)
        >> (stween(30, frame_number=T//4*3, ease='quad_out') >> stween(30, frame_number=0, ease='cubic')) + (
            stween(60)
            # >> chat_step2
            >> stween(20, hand_dy=10, hand_dx=0, hand_size=1, hand_alpha=1.0, ease='cubic')
            >> stween(hand_grabbing=True)
        )
        >> cstween(30, target_trails_alpha = 1., track_alpha = 1.) + (stween(30) >> play_video)
        >> (tween(T*2) >> tween(T*2,  **status_output_state, ease='cubic') + (tween(T)>>tween(T, status_text=status_output_str)))+ (
               play_video
            >> play_video + ctween(T-1, blended_trails_alpha = 0, counter_trails_alpha = 0, target_trails_alpha = 0)
            >> play_video + ctween(T-1, arrows_alpha = 0)
            >> play_video + ctween(T-1, hand_alpha = 0)
            >> play_video
            >> play_video + ctween(T-1, circles_alpha = 0)
            >> play_video
            >> play_video
        )





        # >> play_video + 
        # >> stween(T - 1, frame_number=T - 1) + stween(T - 1, circles_alpha=1)
        # >> stween(T//4, hand_alpha=1, hand_grabbing=True, hand_dx=10, hand_dy=-10, hand_size=0.8)
        # >> stween(T//8, chat_alpha=1, chat_text="Welcome to the demo!", chat_width=500)


        # >> stween(T - 1, frame_number=T - 1) + stween(T//2, status_width=300, status_alpha=1, status_offset=30, ease='cubic')
        # >> stween(frame_number=0, track_numbers=[0, 1, 2])
        # >> stween(T - 1, frame_number=T - 1) + stween(T - 1, circles_alpha=1)
        # >> stween(T//4, hand_alpha=1, hand_grabbing=True, hand_dx=10, hand_dy=-10, hand_size=0.8)
    )

    mo.md(f"Timeline Length: {len(timeline)}")
    return default_frame_number, timeline


@app.cell
def _(
    get_frame,
    mo,
    preview_frame_slider,
    render_end_slider,
    render_start_slider,
    render_video_button,
    timeline,
):
    frame_number = preview_frame_slider.value
    state = timeline[preview_frame_slider.value]
    frame = get_frame(frame_number)

    mo.vstack(
        [
            mo.image(frame, width=720),
            preview_frame_slider,
            render_video_button,
            render_start_slider,
            render_end_slider,
        ],
    )
    return


@app.cell
def _(final_frame, rp, timeline):
    def get_frame(frame_number):
        state = timeline[frame_number]
        frame = final_frame(**state)
        return frame


    def get_video(render_start=None, render_end=None):
        for frame_number in rp.eta(range(render_start, render_end),  "Rendering"):
            yield get_frame(frame_number)
        # for state in rp.eta(timeline, "Rendering"):
        #     frame = final_frame(**state)
        #     yield frame
    return get_frame, get_video


@app.cell
def _(default_frame_number, mo, partial, timeline):
    make_frame_slider = partial(mo.ui.slider, include_input=True,debounce=False,full_width=True,step=1)

    preview_frame_slider = make_frame_slider(
        start=0,
        stop=len(timeline) - 1,
        value=default_frame_number,
        label="Frame Number:",
    )

    render_start_slider = make_frame_slider(
        start=0,
        stop=len(timeline) - 1,
        value=0,
        label="Render Start:",
    )


    render_end_slider = make_frame_slider(
        start=0,
        stop=len(timeline),
        value=len(timeline),
        label="Render End:",
    )

    render_video_button = mo.ui.run_button(label="Render Video")
    return (
        preview_frame_slider,
        render_end_slider,
        render_start_slider,
        render_video_button,
    )


@app.cell
def _(
    get_video,
    render_end_slider,
    render_start_slider,
    render_video_button,
    rp,
):
    video_path = None
    if render_video_button.value:
        render_start = render_start_slider.value
        render_end = render_end_slider.value
        video = get_video(render_start, render_end)
        video_path = rp.save_video_mp4(video, show_progress=False, framerate=60)
        rp.open_file_with_default_application(video_path)
    video_path
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
