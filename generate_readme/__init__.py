#!/usr/bin/env python3
"""
Auto-generate README.md by running each demo and capturing output images.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def run_demo_and_capture(demo_dir, demo_name):
    """Run a demo function and capture its result image."""
    print(f"Processing {demo_name} demo...")
    
    # Change to demo directory for imports to work
    original_cwd = os.getcwd()
    os.chdir(demo_dir)
    
    try:
        if demo_name == "film_strip":
            from rp import load_video
            from film_strip import film_strip
            
            # Use default values from the demo
            video_path = "/Users/ryan/Downloads/StillPepper.mp4"
            try:
                video = load_video(video_path, use_cache=True)
                result = film_strip(video, length=4, height=480, width=720)
                return result
            except Exception as e:
                print(f"Warning: Could not load video for film_strip demo: {e}")
                return None
                
        elif demo_name == "labeled_circle":
            import rp
            from labeled_circle import labeled_circle
            
            # Use default values from the demo
            fill_color = rp.as_rgba_float_color("#00FF00")  # Green
            rim_color = rp.as_rgba_float_color("#FF0000")   # Red
            
            result = labeled_circle(
                text="42",
                color=fill_color,
                rim_color=rim_color,
                rim_width=-20,
                diameter=257,
                padding=10,
                font="Futura",
                text_color="#000000",
                font_size=167,
                text_style="bold",
                with_checkerboard=True,
                crop_zeros=False
            )
            return result
            
        elif demo_name == "image_stack":
            from rp import load_video, blend_images, as_rgb_image, as_byte_image
            import rp
            from image_stack import create_image_stack
            
            # Use default values from the demo
            video_path = "/Users/ryan/Downloads/StillPepper.mp4"
            try:
                video = load_video(video_path, use_cache=True)
                result = create_image_stack(
                    video,
                    num_frames=10,
                    total_shift_x=200,
                    total_shift_y=200,
                    frame_size=256,
                    alphas_exponent=0.5,
                    shadow_shift=10,
                    shadow_blur=30,
                    shadow_opacity=0.25,
                    shadow_color="#000000"
                )
                
                final_result = blend_images("#0000FF", result)
                if True:  # with_alpha_checkerboard default
                    final_result = rp.with_alpha_checkerboard(final_result)
                final_result = as_byte_image(final_result, copy=False)
                
                return final_result
            except Exception as e:
                print(f"Warning: Could not load video for image_stack demo: {e}")
                return None
                
        elif demo_name == "arrow":
            import rp
            from arrow import skia_draw_arrow
            
            # Create canvas with 5 arrow variants side by side
            canvas_width, canvas_height = 1000, 300
            canvas = rp.as_rgba_image(rp.uniform_float_color_image(canvas_height, canvas_width, 'white'), copy=False)
            
            # Define 5 arrow variants side by side
            arrow_spacing = canvas_width // 5
            arrow_y = canvas_height // 2
            
            arrows = [
                # Arrow 1: Classic solid arrow with shadow
                {
                    'x0': arrow_spacing * 0 + 50,
                    'x1': arrow_spacing * 1 - 50,
                    'y0': arrow_y,
                    'y1': arrow_y,
                    'fill': '#4A90E2',
                    'stroke': True,
                    'stroke_color': '#2C3E50',
                    'stroke_width': 2,
                    'shadow': True,
                    'shadow_dx': 3,
                    'shadow_dy': 3,
                    'shadow_blur': 5,
                    'shadow_opacity': 0.4
                },
                
                # Arrow 2: Dashed stroke, no fill
                {
                    'x0': arrow_spacing * 1 + 50,
                    'x1': arrow_spacing * 2 - 50,
                    'y0': arrow_y,
                    'y1': arrow_y,
                    'fill': None,
                    'stroke': True,
                    'stroke_color': '#E74C3C',
                    'stroke_width': 4,
                    'stroke_type': 'dashed',
                    'stroke_cap': 'round',
                    'stroke_join': 'round'
                },
                
                # Arrow 3: Thick dotted stroke with unique shape
                {
                    'x0': arrow_spacing * 2 + 50,
                    'x1': arrow_spacing * 3 - 50,
                    'y0': arrow_y,
                    'y1': arrow_y,
                    'tip_width': 25,
                    'tip_height': 20,
                    'tip_dimple': 8,
                    'end_width': 8,
                    'start_width': 4,
                    'fill': '#9B59B6',
                    'stroke': True,
                    'stroke_color': '#8E44AD',
                    'stroke_width': 3,
                    'stroke_type': 'dotted',
                    'stroke_cap': 'round'
                },
                
                # Arrow 4: Gradient-like effect with custom dash pattern
                {
                    'x0': arrow_spacing * 3 + 50,
                    'x1': arrow_spacing * 4 - 50,
                    'y0': arrow_y,
                    'y1': arrow_y,
                    'tip_width': 20,
                    'tip_height': 25,
                    'tip_dimple': 10,
                    'end_width': 12,
                    'start_width': 2,
                    'fill': '#F39C12',
                    'stroke': True,
                    'stroke_color': '#D68910',
                    'stroke_width': 2,
                    'stroke_type': 'dashdot',
                    'shadow': 'both',
                    'shadow_dx': 2,
                    'shadow_dy': 2,
                    'shadow_blur': 8,
                    'shadow_color': '#BDC3C7',
                    'shadow_opacity': 0.6
                },
                
                # Arrow 5: Bold angular arrow
                {
                    'x0': arrow_spacing * 4 + 50,
                    'x1': arrow_spacing * 5 - 50,
                    'y0': arrow_y,
                    'y1': arrow_y,
                    'tip_width': 30,
                    'tip_height': 15,
                    'tip_dimple': 2,
                    'end_width': 15,
                    'start_width': 8,
                    'fill': '#27AE60',
                    'stroke': True,
                    'stroke_color': '#1E8449',
                    'stroke_width': 3,
                    'stroke_cap': 'square',
                    'stroke_join': 'miter',
                    'shadow': True,
                    'shadow_dx': 4,
                    'shadow_dy': 4,
                    'shadow_blur': 6,
                    'shadow_opacity': 0.3
                }
            ]
            
            # Draw all arrows
            for arrow_config in arrows:
                canvas = skia_draw_arrow(canvas, **arrow_config, copy=False)
            
            return canvas
            
        elif demo_name == "arrow_animation":
            import rp
            from arrow import skia_draw_arrow
            import math
            
            def lerp(a, b, t):
                """Linear interpolation between a and b"""
                return a + (b - a) * t
            
            def smooth_step(t):
                """Smooth interpolation curve"""
                return t * t * (3 - 2 * t)
            
            # Animation settings
            frames = 100
            canvas_size = 512
            
            # Create frame storage
            animation_frames = []
            
            # Define keyframes with specific settings
            keyframes = [
                # Keyframe 0: Normal arrow
                {
                    'x0': 100, 'y0': 256, 'x1': 400, 'y1': 256,
                    'start_width': 8, 'end_width': 12,
                    'tip_width': 20, 'tip_height': 25, 'tip_dimple': 8,
                    'shadow': True, 'shadow_blur': 5, 'shadow_color': '#000000',
                    'fill': '#4A90E2', 'stroke_color': '#2C3E50'
                },
                
                # Keyframe 1: Both widths = 0 (thin line arrow)
                {
                    'x0': 256, 'y0': 100, 'x1': 256, 'y1': 400,
                    'start_width': 0, 'end_width': 0,
                    'tip_width': 30, 'tip_height': 20, 'tip_dimple': 5,
                    'shadow': True, 'shadow_blur': 8, 'shadow_color': '#FF0000',
                    'fill': '#E74C3C', 'stroke_color': '#C0392B'
                },
                
                # Keyframe 2: Shadow invisible
                {
                    'x0': 400, 'y0': 150, 'x1': 100, 'y1': 350,
                    'start_width': 5, 'end_width': 15,
                    'tip_width': 25, 'tip_height': 30, 'tip_dimple': 10,
                    'shadow': False, 'shadow_blur': 0, 'shadow_color': '#000000',
                    'fill': '#9B59B6', 'stroke_color': '#8E44AD'
                },
                
                # Keyframe 3: High shadow blur
                {
                    'x0': 150, 'y0': 400, 'x1': 350, 'y1': 100,
                    'start_width': 10, 'end_width': 6,
                    'tip_width': 35, 'tip_height': 15, 'tip_dimple': 3,
                    'shadow': True, 'shadow_blur': 20, 'shadow_color': '#00FF00',
                    'fill': '#F39C12', 'stroke_color': '#D68910'
                },
                
                # Keyframe 4: Dimple = 0
                {
                    'x0': 300, 'y0': 450, 'x1': 200, 'y1': 50,
                    'start_width': 12, 'end_width': 8,
                    'tip_width': 28, 'tip_height': 22, 'tip_dimple': 0,
                    'shadow': True, 'shadow_blur': 10, 'shadow_color': '#FF00FF',
                    'fill': '#27AE60', 'stroke_color': '#1E8449'
                },
                
                # Keyframe 5: Dimple = tip_height
                {
                    'x0': 450, 'y0': 300, 'x1': 50, 'y1': 200,
                    'start_width': 4, 'end_width': 16,
                    'tip_width': 20, 'tip_height': 18, 'tip_dimple': 18,
                    'shadow': True, 'shadow_blur': 6, 'shadow_color': '#FFFF00',
                    'fill': '#E67E22', 'stroke_color': '#D35400'
                },
                
                # Keyframe 6: Start width = end width
                {
                    'x0': 380, 'y0': 380, 'x1': 120, 'y1': 120,
                    'start_width': 10, 'end_width': 10,
                    'tip_width': 32, 'tip_height': 28, 'tip_dimple': 12,
                    'shadow': True, 'shadow_blur': 15, 'shadow_color': '#00FFFF',
                    'fill': '#3498DB', 'stroke_color': '#2980B9'
                },
                
                # Keyframe 7: Extreme positions
                {
                    'x0': 50, 'y0': 50, 'x1': 450, 'y1': 450,
                    'start_width': 2, 'end_width': 20,
                    'tip_width': 40, 'tip_height': 35, 'tip_dimple': 15,
                    'shadow': True, 'shadow_blur': 25, 'shadow_color': '#800080',
                    'fill': '#1ABC9C', 'stroke_color': '#16A085'
                },
                
                # Keyframe 8: Curved diagonal
                {
                    'x0': 200, 'y0': 50, 'x1': 300, 'y1': 450,
                    'start_width': 15, 'end_width': 3,
                    'tip_width': 22, 'tip_height': 40, 'tip_dimple': 20,
                    'shadow': True, 'shadow_blur': 3, 'shadow_color': '#FFA500',
                    'fill': '#E91E63', 'stroke_color': '#C2185B'
                },
                
                # Keyframe 9: Back to start-like
                {
                    'x0': 120, 'y0': 256, 'x1': 380, 'y1': 256,
                    'start_width': 6, 'end_width': 14,
                    'tip_width': 24, 'tip_height': 20, 'tip_dimple': 6,
                    'shadow': True, 'shadow_blur': 7, 'shadow_color': '#000000',
                    'fill': '#673AB7', 'stroke_color': '#512DA8'
                }
            ]
            
            num_keyframes = len(keyframes)
            
            for frame_idx in range(frames):
                # Calculate which keyframes to interpolate between
                t = frame_idx / (frames - 1)  # 0 to 1
                keyframe_float = t * (num_keyframes - 1)
                keyframe_idx = int(keyframe_float)
                local_t = keyframe_float - keyframe_idx
                
                # Handle last frame
                if keyframe_idx >= num_keyframes - 1:
                    current_kf = keyframes[-1]
                else:
                    # Interpolate between current and next keyframe
                    current_kf = keyframes[keyframe_idx]
                    next_kf = keyframes[keyframe_idx + 1]
                    
                    # Apply smooth interpolation
                    smooth_t = smooth_step(local_t)
                    
                    # Interpolate all parameters
                    current_kf = {
                        'x0': lerp(current_kf['x0'], next_kf['x0'], smooth_t),
                        'y0': lerp(current_kf['y0'], next_kf['y0'], smooth_t),
                        'x1': lerp(current_kf['x1'], next_kf['x1'], smooth_t),
                        'y1': lerp(current_kf['y1'], next_kf['y1'], smooth_t),
                        'start_width': lerp(current_kf['start_width'], next_kf['start_width'], smooth_t),
                        'end_width': lerp(current_kf['end_width'], next_kf['end_width'], smooth_t),
                        'tip_width': lerp(current_kf['tip_width'], next_kf['tip_width'], smooth_t),
                        'tip_height': lerp(current_kf['tip_height'], next_kf['tip_height'], smooth_t),
                        'tip_dimple': lerp(current_kf['tip_dimple'], next_kf['tip_dimple'], smooth_t),
                        'shadow_blur': lerp(current_kf['shadow_blur'], next_kf['shadow_blur'], smooth_t),
                        'shadow': current_kf['shadow'] if smooth_t < 0.5 else next_kf['shadow'],
                        'shadow_color': current_kf['shadow_color'] if smooth_t < 0.5 else next_kf['shadow_color'],
                        'fill': current_kf['fill'] if smooth_t < 0.5 else next_kf['fill'],
                        'stroke_color': current_kf['stroke_color'] if smooth_t < 0.5 else next_kf['stroke_color'],
                    }
                
                # Create canvas for this frame
                canvas = rp.as_rgba_image(rp.uniform_float_color_image(canvas_size, canvas_size, 'white'), copy=False)
                
                # Draw arrow with current parameters
                canvas = skia_draw_arrow(
                    canvas,
                    x0=current_kf['x0'],
                    y0=current_kf['y0'],
                    x1=current_kf['x1'],
                    y1=current_kf['y1'],
                    start_width=current_kf['start_width'],
                    end_width=current_kf['end_width'],
                    tip_width=current_kf['tip_width'],
                    tip_height=current_kf['tip_height'],
                    tip_dimple=current_kf['tip_dimple'],
                    fill=current_kf['fill'],
                    stroke=True,
                    stroke_color=current_kf['stroke_color'],
                    stroke_width=2,
                    shadow=current_kf['shadow'],
                    shadow_blur=current_kf['shadow_blur'],
                    shadow_color=current_kf['shadow_color'],
                    shadow_dx=3,
                    shadow_dy=3,
                    shadow_opacity=0.5,
                    copy=False
                )
                
                animation_frames.append(canvas)
                if frame_idx % 10 == 0:
                    print(f"Generated animation frame {frame_idx + 1}/{frames}")
            
            # Save the animation and return None to skip PNG generation
            animation_path = str(demo_dir.parent / "assets" / "arrow_animation.gif")
            rp.save_animated_gif(animation_frames, animation_path)
            print(f"Arrow animation saved to: {animation_path}")
            
            # Return None to skip PNG generation - we only want the GIF
            return None
            
        elif demo_name == "image_stack_animation":
            from rp import load_video, blend_images, as_rgb_image, as_byte_image
            import rp
            from image_stack import create_image_stack
            import math
            
            def lerp(a, b, t):
                """Linear interpolation between a and b"""
                return a + (b - a) * t
            
            def smooth_step(t):
                """Smooth interpolation curve"""
                return t * t * (3 - 2 * t)
            
            # Animation settings
            frames = 80
            canvas_size = 400
            
            # Load sample video
            try:
                video = load_video("/Users/ryan/Downloads/StillPepper.mp4", use_cache=True)
            except:
                # Create synthetic video frames if real video unavailable
                video = []
                for i in range(20):
                    angle = i * 18
                    frame = rp.linear_gradient_image(
                        256, 256,
                        [rp.as_rgba_float_color(f'hsl({(angle + j*60) % 360}, 80%, 60%)') for j in range(3)],
                        direction=angle
                    )
                    video.append(frame)
            
            # Create frame storage
            animation_frames = []
            
            # Define keyframes with varying parameters
            keyframes = [
                {
                    'num_frames': 8, 'total_shift_x': 150, 'total_shift_y': 150, 'frame_size': 200,
                    'shadow_shift': 8, 'shadow_blur': 20, 'shadow_opacity': 0.3, 'alphas_exponent': 0.6, 'shadow_color': '#000000'
                },
                {
                    'num_frames': 15, 'total_shift_x': 80, 'total_shift_y': 80, 'frame_size': 180,
                    'shadow_shift': 4, 'shadow_blur': 15, 'shadow_opacity': 0.4, 'alphas_exponent': 0.3, 'shadow_color': '#333333'
                },
                {
                    'num_frames': 5, 'total_shift_x': 300, 'total_shift_y': 100, 'frame_size': 240,
                    'shadow_shift': 15, 'shadow_blur': 35, 'shadow_opacity': 0.5, 'alphas_exponent': 0.8, 'shadow_color': '#FF0000'
                },
                {
                    'num_frames': 10, 'total_shift_x': 50, 'total_shift_y': 250, 'frame_size': 160,
                    'shadow_shift': 20, 'shadow_blur': 25, 'shadow_opacity': 0.2, 'alphas_exponent': 0.4, 'shadow_color': '#0000FF'
                },
                {
                    'num_frames': 12, 'total_shift_x': 200, 'total_shift_y': 200, 'frame_size': 220,
                    'shadow_shift': 6, 'shadow_blur': 40, 'shadow_opacity': 0.6, 'alphas_exponent': 0.9, 'shadow_color': '#00FF00'
                },
                {
                    'num_frames': 8, 'total_shift_x': 280, 'total_shift_y': 40, 'frame_size': 190,
                    'shadow_shift': 12, 'shadow_blur': 18, 'shadow_opacity': 0.35, 'alphas_exponent': 0.5, 'shadow_color': '#FF00FF'
                },
                {
                    'num_frames': 6, 'total_shift_x': 60, 'total_shift_y': 60, 'frame_size': 250,
                    'shadow_shift': 0, 'shadow_blur': 0, 'shadow_opacity': 0.0, 'alphas_exponent': 0.7, 'shadow_color': '#000000'
                },
                {
                    'num_frames': 9, 'total_shift_x': 180, 'total_shift_y': 180, 'frame_size': 170,
                    'shadow_shift': 25, 'shadow_blur': 50, 'shadow_opacity': 0.7, 'alphas_exponent': 0.2, 'shadow_color': '#800080'
                },
                {
                    'num_frames': 10, 'total_shift_x': 120, 'total_shift_y': 120, 'frame_size': 210,
                    'shadow_shift': 10, 'shadow_blur': 22, 'shadow_opacity': 0.25, 'alphas_exponent': 0.55, 'shadow_color': '#000000'
                }
            ]
            
            num_keyframes = len(keyframes)
            
            for frame_idx in range(frames):
                t = frame_idx / (frames - 1)
                keyframe_float = t * (num_keyframes - 1)
                keyframe_idx = int(keyframe_float)
                local_t = keyframe_float - keyframe_idx
                
                if keyframe_idx >= num_keyframes - 1:
                    current_kf = keyframes[-1]
                else:
                    current_kf = keyframes[keyframe_idx]
                    next_kf = keyframes[keyframe_idx + 1]
                    smooth_t = smooth_step(local_t)
                    
                    current_kf = {
                        'num_frames': int(lerp(current_kf['num_frames'], next_kf['num_frames'], smooth_t)),
                        'total_shift_x': lerp(current_kf['total_shift_x'], next_kf['total_shift_x'], smooth_t),
                        'total_shift_y': lerp(current_kf['total_shift_y'], next_kf['total_shift_y'], smooth_t),
                        'frame_size': int(lerp(current_kf['frame_size'], next_kf['frame_size'], smooth_t)),
                        'shadow_shift': lerp(current_kf['shadow_shift'], next_kf['shadow_shift'], smooth_t),
                        'shadow_blur': lerp(current_kf['shadow_blur'], next_kf['shadow_blur'], smooth_t),
                        'shadow_opacity': lerp(current_kf['shadow_opacity'], next_kf['shadow_opacity'], smooth_t),
                        'alphas_exponent': lerp(current_kf['alphas_exponent'], next_kf['alphas_exponent'], smooth_t),
                        'shadow_color': current_kf['shadow_color'] if smooth_t < 0.5 else next_kf['shadow_color'],
                    }
                
                try:
                    result = create_image_stack(
                        video,
                        num_frames=current_kf['num_frames'],
                        total_shift_x=current_kf['total_shift_x'],
                        total_shift_y=current_kf['total_shift_y'],
                        frame_size=current_kf['frame_size'],
                        shadow_shift=current_kf['shadow_shift'],
                        shadow_blur=current_kf['shadow_blur'],
                        shadow_opacity=current_kf['shadow_opacity'],
                        alphas_exponent=current_kf['alphas_exponent'],
                        shadow_color=current_kf['shadow_color']
                    )
                    
                    final_result = blend_images("#0000FF", result)
                    final_result = rp.with_alpha_checkerboard(final_result)
                    final_result = as_byte_image(final_result, copy=False)
                    final_result = rp.resize_image_to_fit(final_result, canvas_size, canvas_size)
                    final_result = rp.as_rgba_image(final_result, copy=False)
                    animation_frames.append(final_result)
                    
                except Exception as e:
                    print(f"Error creating frame {frame_idx}: {e}")
                    blank = rp.as_rgba_image(rp.uniform_float_color_image(canvas_size, canvas_size, 'white'), copy=False)
                    animation_frames.append(blank)
                
                if frame_idx % 10 == 0:
                    print(f"Generated image stack animation frame {frame_idx + 1}/{frames}")
            
            # Save the animation and return None to skip PNG generation
            animation_path = str(demo_dir.parent / "assets" / "image_stack_animation.gif")
            rp.save_animated_gif(animation_frames, animation_path)
            print(f"Image stack animation saved to: {animation_path}")
            
            # Return None to skip PNG generation - we only want the GIF
            return None
                
    finally:
        os.chdir(original_cwd)
    
    return None

def main():
    """Generate README.md with demo images."""
    base_dir = Path(__file__).parent
    assets_dir = base_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Find all demo directories
    demo_dirs = []
    for item in base_dir.iterdir():
        if item.is_dir() and (item / f"{item.name}_demo.py").exists():
            demo_dirs.append(item)
    
    demo_dirs = sorted(demo_dirs, key=lambda x: x.name)
    
    readme_content = ["# FigureSnippets", "", "Image and video processing utilities for creating visual effects.", ""]
    
    # Process each demo
    for demo_dir in demo_dirs:
        demo_name = demo_dir.name
        print(f"\\nProcessing {demo_name} demo...")
        
        # Run demo and capture result
        result_image = run_demo_and_capture(demo_dir, demo_name)
        
        if demo_name in ["arrow_animation", "image_stack_animation"]:
            # Use the GIF directly
            gif_filename = f"{demo_name}.gif"
            title = demo_name.replace("_", " ").title()
            readme_content.extend([
                f"## {title}",
                "",
                f"![{title}](assets/{gif_filename})",
                ""
            ])
        elif result_image is not None:
            # Save image to assets
            image_filename = f"{demo_name}_demo.png"
            image_path = assets_dir / image_filename
            
            # Import rp to save image
            import rp
            rp.save_image(result_image, str(image_path))
            print(f"Saved {image_filename}")
            
            # Add to README
            title = demo_name.replace("_", " ").title()
            readme_content.extend([
                f"## {title}",
                "",
                f"![{title}](assets/{image_filename})",
                ""
            ])
        else:
            print(f"Skipped {demo_name} (could not generate image)")
    
    # Add usage section
    readme_content.extend([
        "## Usage",
        "",
        "```python",
        "from FigureSnippets import film_strip, labeled_circle, create_image_stack, skia_draw_arrow",
        "```",
        "",
        "Run interactive demos:",
        "```bash",
        "cd film_strip/ && marimo run film_strip_demo.py",
        "cd labeled_circle/ && marimo run labeled_circle_demo.py", 
        "cd image_stack/ && marimo run image_stack_demo.py",
        "cd arrow/ && marimo run arrow_demo.py",
        "```"
    ])
    
    # Write README.md
    readme_path = base_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write("\n".join(readme_content))
    
    print(f"\\nGenerated {readme_path}")

if __name__ == "__main__":
    main()