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

    from fullvid import final_frame, N, T, H, W
    return N, T, final_frame, mo, rp, tween


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
            ]
        }
    )
    track_checkboxes = [
        mo.ui.checkbox(value=True, label=str(i + 1)) for i in range(N)
    ]
    return controls, track_checkboxes


@app.cell
def _(T, mo, tween):
    # Animation Definition
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
            hand_grabbing=False,
            hand_alpha=0.0,
            hand_dx=0,
            hand_dy=0,
            hand_size=1.0,
            status_width=0,
            status_offset=0.0, 
            status_alpha =0.0,
            status_text="Input Video",
            status_color="dark green",
            track_numbers=[],
        )
        >> ((( tween(T - 1, frame_number=T - 1) >> tween(frame_number=0, track_numbers=[0, 1, 2]) )  )
           + tween(T//2, status_width=300, status_alpha=1, status_offset=30, ease='cubic'))

        >> tween(T - 1, frame_number=T - 1) + tween(T - 1, circles_alpha=1)
        >> tween(T//4, hand_alpha=1, hand_grabbing=True, hand_dx=10, hand_dy=-10, hand_size=0.8)


        # >> tween(T - 1, frame_number=T - 1) + tween(T//2, status_width=300, status_alpha=1, status_offset=30, ease='cubic')
        # >> tween(frame_number=0, track_numbers=[0, 1, 2])
        # >> tween(T - 1, frame_number=T - 1) + tween(T - 1, circles_alpha=1)
        # >> tween(T//4, hand_alpha=1, hand_grabbing=True, hand_dx=10, hand_dy=-10, hand_size=0.8)
    )

    mo.md(f"Timeline Length: {len(timeline)}")
    return (timeline,)


@app.cell
def _(get_frame, mo, preview_frame_slider, render_video_button, timeline):
    frame_number = preview_frame_slider.value
    state = timeline[preview_frame_slider.value]
    frame = get_frame(frame_number)

    mo.vstack(
        [
            mo.image(frame, width=720),
            preview_frame_slider,
            render_video_button,
        ],
    )
    return


@app.cell
def _(final_frame, rp, timeline):
    def get_frame(frame_number):
        state = timeline[frame_number]
        frame = final_frame(**state)
        return frame


    def get_video():
        for state in rp.eta(timeline, "Rendering"):
            frame = final_frame(**state)
            yield frame
    return get_frame, get_video


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
