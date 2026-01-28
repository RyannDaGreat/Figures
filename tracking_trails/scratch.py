import os
import sys
import argparse
import numpy as np
import cv2
import skia
from tqdm import tqdm

# Handle MoviePy versions safely
try:
    from moviepy.editor import VideoFileClip, ImageSequenceClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

# ==========================================
# 1. VISUALIZER CLASS
# ==========================================

class Visualizer:
    def __init__(
        self,
        save_dir: str = "./results",
        pad_value: int = 0,
        fps: int = 24,
        linewidth: int = 2,
        tracks_leave_trace: int = 0,
    ):
        self.save_dir = save_dir
        self.tracks_leave_trace = tracks_leave_trace
        self.pad_value = pad_value
        self.linewidth = linewidth
        self.fps = fps

    def visualize(
        self,
        video: np.ndarray,      # (T, H, W, C) - used for dimensions, can be blank
        tracks: np.ndarray,     # (T, N, 3) -> UVZ
        visibility: np.ndarray = None,
        filename: str = "video",
        save_video: bool = True,
        original_video: np.ndarray = None,  # For overlay compositing
    ):
        # Pad video if required
        if self.pad_value > 0:
            video = np.pad(
                video,
                ((0,0), (self.pad_value, self.pad_value), (self.pad_value, self.pad_value), (0,0)),
                mode='constant',
                constant_values=255
            )
            tracks = tracks.copy()
            tracks[..., :2] = tracks[..., :2] + self.pad_value
            if original_video is not None:
                original_video = np.pad(
                    original_video,
                    ((0,0), (self.pad_value, self.pad_value), (self.pad_value, self.pad_value), (0,0)),
                    mode='constant',
                    constant_values=0
                )

        # Returns BGRA frames
        tracked_frames = self.draw_tracks_on_video(
            video=video,
            tracks=tracks,
            visibility=visibility,
        )

        if save_video:
            # Save on white background
            self.save_video(tracked_frames, filename=filename, savedir=self.save_dir)

            # Save overlay on original video if provided, at multiple opacities
            if original_video is not None:
                overlay_opacities = [1.0, 0.75, 0.5]
                for opacity in overlay_opacities:
                    opacity_pct = int(opacity * 100)
                    overlay_filename = filename.replace('.mp4', f'_overlay_{opacity_pct}pct.mp4')
                    self.save_video(tracked_frames, filename=overlay_filename, savedir=self.save_dir,
                                   background_frames=list(original_video), overlay_opacity=opacity)

        return tracked_frames

    def save_video(self, frames, filename, savedir=None, background_frames=None, overlay_opacity=1.0):
        """Save video with RGBA frames composited on background.

        Args:
            frames: List of BGRA numpy arrays with alpha
            filename: Output filename
            savedir: Output directory
            background_frames: Optional list of RGB frames to composite on (for overlay)
            overlay_opacity: Multiplier for the overlay alpha (0.0-1.0)
        """
        if savedir is None:
            savedir = self.save_dir
        os.makedirs(savedir, exist_ok=True)

        save_path = os.path.join(savedir, f"{filename}")

        # Composite BGRA frames onto background
        composited = []
        for i, bgra in enumerate(frames):
            # Extract alpha channel (0-255) and apply opacity multiplier
            alpha = bgra[:, :, 3:4].astype(np.float32) / 255.0 * overlay_opacity
            # BGRA to RGB
            rgb_fg = bgra[:, :, [2, 1, 0]].astype(np.float32)

            if background_frames is not None:
                bg = background_frames[i].astype(np.float32)
            else:
                # White background
                bg = np.full_like(rgb_fg, 255.0)

            # Alpha composite: out = fg * alpha + bg * (1 - alpha)
            result = rgb_fg * alpha + bg * (1.0 - alpha)
            composited.append(result.astype(np.uint8))

        try:
            clip = ImageSequenceClip(composited, fps=self.fps)
            clip.write_videofile(save_path, codec="libx264", bitrate="50M", logger=None)
            print(f"Saved: {save_path}")
        except Exception as e:
            print(f"Error saving video: {e}")

    def draw_tracks_on_video(self, video, tracks, visibility=None):
        """Draw all tracks using Skia only with depth-based parallax."""
        T, H, W, C = video.shape
        _, N, D = tracks.shape

        res_video = []

        # Colors stored as RGB tuples (0-255)
        vector_colors = np.zeros((N, 3))

        # =========================================================
        # Compute global Z range for parallax scaling
        # =========================================================
        all_z = tracks[:, :, 2].flatten()
        z_min_global = np.min(all_z)
        z_max_global = np.max(all_z)
        if z_max_global == z_min_global:
            z_max_global += 1.0

        # =========================================================
        # COLOR LOGIC: Normalize First Appearance (u, v, z)
        # =========================================================

        start_vals = []
        track_indices = []

        for n in range(N):
            f_idx = 0
            if visibility is not None:
                vis_col = visibility[:, n].flatten()
                vis_frames = np.where(vis_col != 0)[0]
                if len(vis_frames) > 0:
                    f_idx = vis_frames[0]
                else:
                    continue

            u, v, z = tracks[f_idx, n]
            start_vals.append([u, v, z])
            track_indices.append(n)

        start_vals = np.array(start_vals) if len(start_vals) > 0 else np.zeros((0, 3))

        # Determine Z range for color normalization
        if len(start_vals) > 0:
            z_vals = start_vals[:, 2]
            z_min, z_max = np.min(z_vals), np.max(z_vals)
            if z_max == z_min:
                z_max += 1.0
        else:
            z_min, z_max = 0.0, 1.0

        # Assign colors (RGB, 0-255)
        for idx, n in enumerate(track_indices):
            u, v, z = start_vals[idx]
            r = int(np.clip(u / max(1, W), 0, 1) * 255)
            g = int(np.clip(v / max(1, H), 0, 1) * 255)
            b = int(np.clip((z - z_min) / (z_max - z_min), 0, 1) * 255)
            vector_colors[n] = [r, g, b]

        # =========================================================

        for t in tqdm(range(T), desc="Rendering Frames"):
            # Create Skia surface with TRANSPARENT background for compositing
            surface = skia.Surface.MakeRasterN32Premul(W, H)
            canvas = surface.getCanvas()
            canvas.clear(skia.ColorTRANSPARENT)

            # Collect all drawable elements with their Z for global sorting
            # Each element: (z, type, data)
            # type: 'segment' or 'dot'
            draw_list = []

            first_ind = max(0, t - self.tracks_leave_trace) if self.tracks_leave_trace > 0 else 0
            tracks_slice = tracks[first_ind : t + 1]
            vis_slice = visibility[first_ind : t + 1] if visibility is not None else None
            T_slice = tracks_slice.shape[0]

            num_substeps = 8
            max_width = self.linewidth * 2

            for i in range(N):
                x, y, z = tracks[t, i, 0], tracks[t, i, 1], tracks[t, i, 2]
                r, g, b = vector_colors[i]

                # Collect trail segments (draw even if current head is not visible)
                if self.tracks_leave_trace != 0 and T_slice >= 2:
                    points = []
                    for s in range(T_slice):
                        sx, sy, sz = tracks_slice[s, i, 0], tracks_slice[s, i, 1], tracks_slice[s, i, 2]
                        is_vis = True
                        if vis_slice is not None:
                            is_vis = vis_slice[s, i].item() > 0
                        if is_vis and (sx, sy) != (0, 0):
                            points.append((s, sx, sy, sz))

                    if len(points) >= 2:
                        for idx in range(len(points) - 1):
                            s1, x1, y1, z1 = points[idx]
                            s2, x2, y2, z2 = points[idx + 1]

                            for sub in range(num_substeps):
                                t0 = sub / num_substeps
                                t1 = (sub + 1) / num_substeps
                                t_avg = (t0 + t1) / 2

                                px1 = x1 + (x2 - x1) * t0
                                py1 = y1 + (y2 - y1) * t0
                                px2 = x1 + (x2 - x1) * t1
                                py2 = y1 + (y2 - y1) * t1

                                z_interp = z1 + (z2 - z1) * t_avg
                                z_norm = 1.0 - (z_interp - z_min_global) / (z_max_global - z_min_global)
                                depth_scale = 0.3 + 0.7 * z_norm

                                progress = (s1 + t_avg) / (T_slice - 1)
                                alpha = (progress ** 1.5) * depth_scale
                                width = max(0.5, max_width * progress * depth_scale)

                                if alpha < 0.02:
                                    continue

                                draw_list.append((z_interp, 'segment', (px1, py1, px2, py2, width, alpha, r, g, b)))

                # Collect dot (only if current position is visible and in bounds)
                is_visible_now = True
                if visibility is not None:
                    is_visible_now = visibility[t, i].item() > 0

                if is_visible_now and 0 <= x < W and 0 <= y < H:
                    z_norm = 1.0 - (z - z_min_global) / (z_max_global - z_min_global)
                    depth_scale = 0.3 + 0.7 * z_norm
                    radius = self.linewidth * 2 * depth_scale
                    draw_list.append((z, 'dot', (x, y, radius, r, g, b)))

            # Sort by Z descending (far first, close on top)
            draw_list.sort(key=lambda item: -item[0])

            # Draw all elements in Z order
            for z_val, elem_type, data in draw_list:
                if elem_type == 'segment':
                    px1, py1, px2, py2, width, alpha, r, g, b = data
                    paint = skia.Paint()
                    paint.setAntiAlias(True)
                    paint.setStyle(skia.Paint.kStroke_Style)
                    paint.setStrokeWidth(width)
                    paint.setStrokeCap(skia.Paint.kRound_Cap)
                    paint.setColor(skia.Color(int(r), int(g), int(b), int(alpha * 255)))
                    canvas.drawLine(px1, py1, px2, py2, paint)
                else:  # dot
                    x, y, radius, r, g, b = data
                    # Fill
                    fill_paint = skia.Paint()
                    fill_paint.setAntiAlias(True)
                    fill_paint.setStyle(skia.Paint.kFill_Style)
                    fill_paint.setColor(skia.Color(int(r), int(g), int(b), 255))
                    canvas.drawCircle(float(x), float(y), float(radius), fill_paint)
                    # Stroke (20% white border)
                    stroke_paint = skia.Paint()
                    stroke_paint.setAntiAlias(True)
                    stroke_paint.setStyle(skia.Paint.kStroke_Style)
                    stroke_paint.setStrokeWidth(1.0)
                    stroke_paint.setColor(skia.Color(255, 255, 255, 51))
                    canvas.drawCircle(float(x), float(y), float(radius), stroke_paint)

            # Get RGBA result
            img = surface.makeImageSnapshot()
            rgba = img.toarray()  # BGRA format
            res_video.append(rgba)  # Store BGRA with alpha

        return res_video

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def get_video_info(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return {'width': width, 'height': height, 'fps': fps, 'frames': frames}


def load_video_frames(path, max_frames=None):
    """Load video frames as RGB numpy array."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {path}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # BGR to RGB
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if max_frames and len(frames) >= max_frames:
            break

    cap.release()
    return np.array(frames)

def convert_gif_to_mp4(gif_path, mp4_path):
    if os.path.exists(mp4_path):
        return
    print(f"Converting {gif_path} to {mp4_path}...")
    try:
        clip = VideoFileClip(gif_path)
        clip.write_videofile(mp4_path, codec="libx264", logger=None)
        clip.close()
    except Exception as e:
        print(f"Failed to convert GIF: {e}")

def resize_tracks(tracks, target_w, target_h):
    REF_W = 832.0
    REF_H = 480.0
    scale_x = target_w / REF_W
    scale_y = target_h / REF_H
    print(f"  - Rescaling tracks: Scale X={scale_x:.2f}, Scale Y={scale_y:.2f}")
    resized_tracks = tracks.copy()
    resized_tracks[..., 0] *= scale_x
    resized_tracks[..., 1] *= scale_y
    return resized_tracks

# ==========================================
# 3. MAIN LOGIC
# ==========================================

def main(folder_path):
    folder_path = os.path.abspath(folder_path)
    vis_output_dir = os.path.join(folder_path, "vis")

    print(f"Scanning directory: {folder_path}")

    # Find all folders with track.npy files
    track_folders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            track_file = os.path.join(item_path, "tmp", "track.npy")
            if os.path.exists(track_file):
                track_folders.append(item)

    print(f"Found {len(track_folders)} folders with track data")

    # Sort to process vid2sim_interpolate first
    sorted_names = sorted(track_folders, key=lambda x: (0 if 'vid2sim_interpolate' in x else 1, x))

    for name in sorted_names:
        # Look for video in multiple locations (priority order):
        # 1. Root folder: name.mp4 or name.gif
        # 2. Inside tmp folder: video720.mp4
        final_mp4_path = None

        root_mp4 = os.path.join(folder_path, f"{name}.mp4")
        root_gif = os.path.join(folder_path, f"{name}.gif")
        tmp_video = os.path.join(folder_path, name, "tmp", "video720.mp4")

        if os.path.exists(root_mp4):
            final_mp4_path = root_mp4
        elif os.path.exists(root_gif):
            mp4_path = os.path.join(folder_path, f"{name}.mp4")
            convert_gif_to_mp4(root_gif, mp4_path)
            final_mp4_path = mp4_path
        elif os.path.exists(tmp_video):
            final_mp4_path = tmp_video

        if not final_mp4_path:
            print(f"Skipping {name}: No video found")
            continue

        track_file_path = os.path.join(folder_path, name, "tmp", "track.npy")
        
        # track_file_path already verified to exist from the scan above

        print(f"Processing: {name}")

        try:
            track_data = np.load(track_file_path, allow_pickle=True).item()
        except Exception as e:
            print(f"  - Error loading numpy file: {e}")
            continue

        if "uvz" not in track_data:
            print("  - Key 'uvz' not found.")
            continue

        raw_tracks = track_data["uvz"]
        if "vis" in track_data:
            raw_vis = track_data["vis"]
        else:
            raw_vis = np.ones((raw_tracks.shape[0], raw_tracks.shape[1]), dtype=bool)

        info = get_video_info(final_mp4_path)
        if not info:
            continue

        H, W = info['height'], info['width']
        fps = info['fps'] if info['fps'] > 0 else 24
        
        raw_tracks = resize_tracks(raw_tracks, target_w=W, target_h=H)

        T_video = info['frames']
        T_tracks = raw_tracks.shape[0]
        T_common = min(T_video, T_tracks)

        current_tracks = raw_tracks[:T_common]
        current_vis = raw_vis[:T_common]

        # Load original video frames for overlay
        print("  - Loading original video frames...")
        original_frames = load_video_frames(final_mp4_path, max_frames=T_common)

        # White Background (for dimensions only, compositing happens in save_video)
        blank_video = np.ones((T_common, H, W, 3), dtype=np.uint8) * 255

        # Point density variants
        densities = [1.0, 0.5, 0.25, 0.1, 0.05]
        N_total = current_tracks.shape[1]

        for density in densities:
            density_pct = int(density * 100)
            N_subset = max(1, int(N_total * density))

            # Randomly sample points (but consistently across frames)
            np.random.seed(42)  # Reproducible
            point_indices = np.random.choice(N_total, N_subset, replace=False)
            point_indices = np.sort(point_indices)

            tracks_subset = current_tracks[:, point_indices, :]
            vis_subset = current_vis[:, point_indices] if current_vis is not None else None

            density_suffix = f"_{density_pct}pct" if density < 1.0 else ""

            # ==========================================
            # 1. VERSION: NO TRACING (Points Only)
            # ==========================================
            print(f"  - Rendering: Points only ({density_pct}% density, {N_subset} points)...")
            vis_engine_points = Visualizer(
                save_dir=vis_output_dir,
                fps=fps,
                linewidth=2,
                tracks_leave_trace=0
            )
            vis_engine_points.visualize(
                video=blank_video,
                tracks=tracks_subset,
                visibility=vis_subset,
                filename=f"{name}_points{density_suffix}.mp4",
                save_video=True,
                original_video=original_frames,
            )

            # ==========================================
            # 2. VERSION: WITH MOTION TRACING
            # ==========================================
            print(f"  - Rendering: Trails ({density_pct}% density, {N_subset} points)...")
            vis_engine_trails = Visualizer(
                save_dir=vis_output_dir,
                fps=fps,
                linewidth=2,
                tracks_leave_trace=4
            )
            vis_engine_trails.visualize(
                video=blank_video,
                tracks=tracks_subset,
                visibility=vis_subset,
                filename=f"{name}_trails{density_suffix}.mp4",
                save_video=True,
                original_video=original_frames,
            )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path", type=str)
    args = parser.parse_args()

    if os.path.exists(args.folder_path):
        main(args.folder_path)
    else:
        print(f"Folder not found: {args.folder_path}")
