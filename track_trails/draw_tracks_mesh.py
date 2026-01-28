"""
Track visualization using skia_draw_trail for smooth textured ribbons.

Uses rp.skia_draw_trail to render tracks as tapered, gradient trails.
"""

import numpy as np
from tqdm import tqdm

import rp

# Supersampling factor for antialiasing (2 = 2x2 = 4 samples per pixel)
SUPERSAMPLE = 2


def draw_tracks_skia(
    tracks,
    video,
    visible=None,
    color='white',
    trail_length=0,
    dot_size=None,
    trail_size=None,
    size=4,
    background=None,
    rim_opacity=0.5,
    rim_color='white',
    rim_thickness=1,
    supersample=SUPERSAMPLE,
):
    """
    Draw tracked points and motion trails using skia_draw_trail.

    Uses rp.skia_draw_trail to render smooth, tapered textured ribbons
    following each track's motion history. Supersampling provides antialiasing.

    Args:
        tracks: numpy array of shape (T, N, 2) containing (x, y) coordinates.
               T = frames, N = number of points.
        video: numpy array of shape (T, H, W, C) as reference video (uint8, RGB).
        visible: numpy array of shape (T, N) with boolean/numeric visibility.
                If None, all points are visible.
        color: Color specification (string, hex, tuple). Passed to rp.as_rgba_float_color.
        trail_length: Number of historical frames to show in trail (0 = dots only).
        dot_size: Radius multiplier for current position dot. If None, uses size parameter.
        trail_size: Width multiplier for trail lines. If None, uses size parameter.
        size: Base size for both dot and trail (default 4). Overridden by dot_size/trail_size.
        background: Background frames to composite onto (default: original video).
        rim_opacity: Opacity of dot border (0-1, default 0.5).
        rim_color: Color of dot border (default 'white').
        rim_thickness: Thickness of dot border in pixels (default 1).
        supersample: Supersampling factor for antialiasing (default 2). Set to 1 to disable.

    Returns:
        numpy array of shape (T, H, W, 4) with RGBA frames ready for video output.
    """
    import skia

    # Convert torch tensors to numpy
    tracks = rp.as_numpy_array(tracks)
    video = rp.as_numpy_array(video)

    T, N, H, W, C = rp.validate_tensor_shapes(
        tracks="T N 2",
        video="T H W C",
        XY=2,
        return_dims="T N H W C",
    )

    if visible is None:
        visible = np.ones((T, N), dtype=bool)
    visible = rp.as_numpy_array(visible)
    assert visible.shape == (T, N), visible.shape

    if background is None:
        background = video

    # Supersampled dimensions
    ss = supersample
    H_ss, W_ss = H * ss, W * ss

    # Get colors as float RGBA
    rgba_float = rp.as_rgba_float_color(color)
    rim_rgba_float = rp.as_rgba_float_color(rim_color)

    # Convert to byte RGB for skia dots
    rgb_byte = rp.float_color_to_byte_color(rgba_float[:3])
    r, g, b = rgb_byte
    rim_rgb_byte = rp.float_color_to_byte_color(rim_rgba_float[:3])
    rim_r, rim_g, rim_b = rim_rgb_byte

    # Resolve dot and trail sizes (scaled for supersampling)
    actual_dot_size = (dot_size if dot_size is not None else size) * ss
    actual_trail_size = (trail_size if trail_size is not None else size) * ss
    actual_rim_thickness = rim_thickness * ss

    # Create trail texture for skia_draw_trail
    # The texture gets transposed internally: texture.transpose(1,0,2)
    # After transpose: original width -> new height (U, along trail), original height -> new width (V, across ribbon)
    # So gradient along original WIDTH maps to U (along the trail path)
    tex_height = 8    # Across ribbon (becomes V after transpose)
    tex_width = 256   # Along trail (becomes U after transpose)

    # Gradient goes left-to-right (along width) = along trail after transpose
    # Empirically determined: left=opaque (head), right=transparent (tail)
    trail_texture = rp.linear_gradient_image(
        tex_height,  # height
        tex_width,   # width
        [
            (rgba_float[0], rgba_float[1], rgba_float[2], 1.0),  # Left: opaque (head)
            (rgba_float[0], rgba_float[1], rgba_float[2], 0.0),  # Right: transparent (tail)
        ],
        direction='horizontal',
    )
    trail_texture = rp.as_byte_image(trail_texture, copy=False)
    trail_texture = rp.as_rgba_image(trail_texture, copy=False)

    res_video = []

    for t in tqdm(range(T), desc="Drawing Tracks (Skia)"):
        # Create supersampled RGBA canvas from background frame
        bg_frame = background[t]
        if ss > 1:
            bg_frame_ss = rp.resize_image(bg_frame, (H_ss, W_ss))
        else:
            bg_frame_ss = bg_frame
        canvas = rp.as_rgba_image(bg_frame_ss, copy=True)

        # Determine historical range for this frame
        first_frame = max(0, t - trail_length) if trail_length > 0 else t
        trail_start = first_frame
        trail_end = t + 1
        trail_length_actual = trail_end - trail_start

        for i in range(N):
            # Current position and visibility (scaled for supersampling)
            x_now = tracks[t, i, 0] * ss
            y_now = tracks[t, i, 1] * ss
            is_visible_now = visible[t, i].item()

            # Draw trail using skia_draw_trail
            if trail_length > 0 and trail_length_actual >= 2:
                # Collect visible points in the trail (scaled for supersampling)
                points = []
                for s in range(trail_start, trail_end):
                    x_hist = tracks[s, i, 0] * ss
                    y_hist = tracks[s, i, 1] * ss
                    is_vis = visible[s, i].item()

                    if is_vis and (x_hist != 0 or y_hist != 0):
                        points.append([x_hist, y_hist])

                if len(points) >= 2:
                    contour = np.array(points, dtype=np.float32)

                    # Resample for smoother rendering
                    contour = rp.evenly_split_path(contour, max(len(contour) * 4, 20), loop=False)
                    n_pts = len(contour)

                    # Taper: inner/outer radius go from 0 at tail to actual_trail_size at head
                    progress = np.linspace(0, 1, n_pts, dtype=np.float32)
                    taper = progress ** 1.5
                    radius = actual_trail_size * taper

                    canvas = rp.skia_draw_trail(
                        canvas,
                        contour,
                        trail_texture,
                        thickness=None,
                        alpha=1.0,
                        loop=False,
                        mode=None,
                        copy=False,
                        inner_radius=radius,
                        outer_radius=radius,
                        interp='bilinear',
                        mipmap=False,
                    )

            # Draw current position dot using skia
            if is_visible_now and 0 <= x_now < W_ss and 0 <= y_now < H_ss:
                # Create skia surface from canvas
                surface = skia.Surface.MakeRasterDirect(
                    skia.ImageInfo.Make(W_ss, H_ss, skia.kRGBA_8888_ColorType, skia.kUnpremul_AlphaType),
                    canvas
                )
                skia_canvas = surface.getCanvas()

                # Fill
                fill_paint = skia.Paint()
                fill_paint.setAntiAlias(True)
                fill_paint.setStyle(skia.Paint.kFill_Style)
                fill_paint.setColor(skia.Color(int(r), int(g), int(b), 255))
                skia_canvas.drawCircle(float(x_now), float(y_now), float(actual_dot_size), fill_paint)

                # Rim border
                stroke_paint = skia.Paint()
                stroke_paint.setAntiAlias(True)
                stroke_paint.setStyle(skia.Paint.kStroke_Style)
                stroke_paint.setStrokeWidth(actual_rim_thickness)
                stroke_paint.setColor(skia.Color(rim_r, rim_g, rim_b, int(rim_opacity * 255)))
                skia_canvas.drawCircle(float(x_now), float(y_now), float(actual_dot_size), stroke_paint)

        # Downsample back to original resolution
        if ss > 1:
            canvas = rp.resize_image(canvas, (H, W))
            canvas = rp.as_byte_image(canvas, copy=False)

        res_video.append(canvas)

    return np.array(res_video, dtype=np.uint8)


def demo_skia():
    """
    Demonstration of track visualization using skia_draw_trail.

    Loads a video, runs CoTracker, visualizes tracks with skia ribbons, and saves output.
    """
    video = rp.load_video(
        'https://warpyournoise.github.io/docs/assets/videos/DeepFloyd/carturn_st_oilpaint_input.mp4',
        use_cache=True,
    )
    print(f"Video shape: {video.shape}, dtype: {video.dtype}")

    tracks, visible = rp.run_cotracker(video, grid_size=7)
    print(f"Tracks shape: {tracks.shape}, dtype: {tracks.dtype}")
    print(f"Visible shape: {visible.shape}, dtype: {visible.dtype}")

    vis_video = draw_tracks_skia(
        tracks,
        video,
        visible,
        color='cyan',
        trail_length=8,
        dot_size=5,
        trail_size=6,
    )
    print(f"Visualized video shape: {vis_video.shape}")

    output_path = 'track_trails_skia_demo.mp4'
    rp.save_video_mp4(vis_video, path=output_path, video_bitrate=10**8)
    print(f"Saved: {output_path}")

    return output_path


if __name__ == '__main__':
    demo_skia()
