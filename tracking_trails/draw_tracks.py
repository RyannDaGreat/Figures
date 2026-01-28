"""
Track visualization for video sequences.

Provides simple, flexible track drawing with motion trails.
"""

import numpy as np
import skia
from tqdm import tqdm

import rp

# Number of sub-segments to interpolate between consecutive track points
# for smooth line rendering. Higher values = smoother trails but slower rendering.
TRAIL_SUBSTEPS = 4


def draw_tracks(
    tracks,
    video,
    visible=None,
    color='white',
    trail_length=0,
    dot_size=None,
    trail_size=None,
    size=4,
    background=None,
):
    """
    Draw tracked points and motion trails on video frames.

    Renders motion trails that taper in opacity and width from head to tail.
    Flexible color input via rp.as_rgba_float_color (supports strings like
    'green', hex codes, RGB tuples, etc.).

    Args:
        tracks: numpy array of shape (T, N, 2) containing (x, y) coordinates.
               T = frames, N = number of points.
        video: numpy array of shape (T, H, W, C) as reference video (uint8, RGB).
        visible: numpy array of shape (T, N) with boolean/numeric visibility.
                If None, all points are visible.
        color: Color specification (string, hex, tuple). Passed to rp.as_rgba_float_color.
               Examples: 'green', '#ff0000', (1.0, 0.5, 0.0), (0.5, 0.5, 0.5, 0.8).
        trail_length: Number of historical frames to show in trail (0 = dots only).
        dot_size: Radius multiplier for current position dot. If None, uses size parameter.
        trail_size: Width multiplier for trail lines. If None, uses size parameter.
        size: Base size for both dot and trail (default 4). Overridden by dot_size/trail_size.
        background: Background frames to composite onto (default: original video).

    Returns:
        numpy array of shape (T, H, W, 4) with BGRA frames ready for video output.

    Examples:
        >>> video = rp.load_video('video.mp4')
        >>> tracks, visible = rp.run_cotracker(video, grid_size=7)
        >>> vis_video = rp.draw_tracks(tracks, video, visible, color='green', trail_length=5)
        >>> rp.save_video_mp4(vis_video, 'output.mp4')

        >>> # Custom sizes
        >>> vis_video = rp.draw_tracks(
        ...     tracks, video, visible,
        ...     color='#00ff00',
        ...     trail_length=10,
        ...     dot_size=6,
        ...     trail_size=2,
        ... )
    """

    # Validate shapes
    T, N, H, W, C = rp.validate_tensor_shapes(
        tracks="T N 2",
        video="T H W C",
        visible="T N",
        XY=2,
        C=3,
        return_dims="T N H W C",
    )

    # Fill in missing visibility
    if visible is None:
        visible = np.ones((T, N), dtype=bool)

    # Set background
    if background is None:
        background = video

    # Convert color to byte RGB
    rgba_float = rp.as_rgba_float_color(color)
    rgb_byte = rp.float_color_to_byte_color(rgba_float[:3])
    r, g, b = rgb_byte

    # Resolve dot and trail sizes
    actual_dot_size = dot_size if dot_size is not None else size
    actual_trail_size = trail_size if trail_size is not None else size

    res_video = []

    for t in tqdm(range(T), desc="Drawing Tracks"):
        # Create transparent surface
        surface = skia.Surface.MakeRasterN32Premul(W, H)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorTRANSPARENT)

        # Determine historical range for this frame
        first_frame = max(0, t - trail_length) if trail_length > 0 else t
        trail_start = first_frame
        trail_end = t + 1
        trail_length_actual = trail_end - trail_start

        for i in range(N):
            # Current position and visibility
            x_now = tracks[t, i, 0]
            y_now = tracks[t, i, 1]
            is_visible_now = visible[t, i].item() > 0 if visible is not None else True

            # Draw trail
            if trail_length > 0 and trail_length_actual >= 2:
                # Collect visible points in the trail
                points = []
                for s in range(trail_start, trail_end):
                    x_hist = tracks[s, i, 0]
                    y_hist = tracks[s, i, 1]
                    is_vis = visible[s, i].item() > 0 if visible is not None else True

                    if is_vis and (x_hist != 0 or y_hist != 0):
                        points.append((x_hist, y_hist))

                # Draw segments between consecutive points
                if len(points) >= 2:
                    for idx in range(len(points) - 1):
                        x1, y1 = points[idx]
                        x2, y2 = points[idx + 1]

                        # Subdivide segment for smooth tapering
                        for sub in range(TRAIL_SUBSTEPS):
                            t0 = sub / TRAIL_SUBSTEPS
                            t1 = (sub + 1) / TRAIL_SUBSTEPS
                            t_mid = (t0 + t1) / 2

                            # Interpolate position
                            px1 = x1 + (x2 - x1) * t0
                            py1 = y1 + (y2 - y1) * t0
                            px2 = x1 + (x2 - x1) * t1
                            py2 = y1 + (y2 - y1) * t1

                            # Progress through entire trail (0 to 1)
                            progress = (idx + t_mid) / (len(points) - 1)

                            # Taper: alpha and width increase from tail to head
                            alpha = (progress ** 1.5)
                            width = actual_trail_size * progress

                            if alpha < 0.02:
                                continue

                            # Draw line segment
                            paint = skia.Paint()
                            paint.setAntiAlias(True)
                            paint.setStyle(skia.Paint.kStroke_Style)
                            paint.setStrokeWidth(width)
                            paint.setStrokeCap(skia.Paint.kRound_Cap)
                            paint.setColor(skia.Color(int(r), int(g), int(b), int(alpha * 255)))
                            canvas.drawLine(px1, py1, px2, py2, paint)

            # Draw current position dot
            if is_visible_now and 0 <= x_now < W and 0 <= y_now < H:
                radius = actual_dot_size

                # Fill
                fill_paint = skia.Paint()
                fill_paint.setAntiAlias(True)
                fill_paint.setStyle(skia.Paint.kFill_Style)
                fill_paint.setColor(skia.Color(int(r), int(g), int(b), 255))
                canvas.drawCircle(float(x_now), float(y_now), float(radius), fill_paint)

                # White border
                stroke_paint = skia.Paint()
                stroke_paint.setAntiAlias(True)
                stroke_paint.setStyle(skia.Paint.kStroke_Style)
                stroke_paint.setStrokeWidth(1.0)
                stroke_paint.setColor(skia.Color(255, 255, 255, 51))
                canvas.drawCircle(float(x_now), float(y_now), float(radius), stroke_paint)

        # Get BGRA frame
        img = surface.makeImageSnapshot()
        bgra = img.toarray()

        # Composite onto background using alpha blending
        alpha = bgra[:, :, 3:4].astype(np.float32) / 255.0  # Extract alpha, normalize to [0, 1]
        rgb_fg = bgra[:, :, [2, 1, 0]].astype(np.float32)  # BGRA to RGB
        rgb_bg = background[t].astype(np.float32)

        # Alpha composite: out = fg * alpha + bg * (1 - alpha)
        composited = rgb_fg * alpha + rgb_bg * (1.0 - alpha)
        composited = np.clip(composited, 0, 255).astype(np.uint8)

        res_video.append(composited)

    return np.array(res_video, dtype=np.uint8)


def demo():
    """
    Demonstration of track visualization workflow.

    Loads a video, runs CoTracker, visualizes tracks, and saves output.
    """
    video = rp.load_video(
        'https://warpyournoise.github.io/docs/assets/videos/DeepFloyd/carturn_st_oilpaint_input.mp4',
        use_cache=True,
    )
    print(f"Video shape: {video.shape}, dtype: {video.dtype}")

    tracks, visible = rp.run_cotracker(video, grid_size=7)
    print(f"Tracks shape: {tracks.shape}, dtype: {tracks.dtype}")
    print(f"Visible shape: {visible.shape}, dtype: {visible.dtype}")

    vis_video = draw_tracks(
        tracks,
        video,
        visible,
        color='green',
        trail_length=5,
        dot_size=4,
    )
    print(f"Visualized video shape: {vis_video.shape}")

    rp.save_video_mp4(vis_video, path='tracking_trails_demo.mp4')
    print("Saved: tracking_trails_demo.mp4")
