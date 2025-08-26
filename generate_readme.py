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
            from image_stack import create_motion_blur_image
            
            # Use default values from the demo
            video_path = "/Users/ryan/Downloads/StillPepper.mp4"
            try:
                video = load_video(video_path, use_cache=True)
                result = create_motion_blur_image(
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
        
        if result_image is not None:
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
        "from FigureSnippets import film_strip, labeled_circle, create_motion_blur_image",
        "```",
        "",
        "Run interactive demos:",
        "```bash",
        "cd film_strip/ && marimo run film_strip_demo.py",
        "cd labeled_circle/ && marimo run labeled_circle_demo.py", 
        "cd image_stack/ && marimo run image_stack_demo.py",
        "```"
    ])
    
    # Write README.md
    readme_path = base_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write("\n".join(readme_content))
    
    print(f"\\nGenerated {readme_path}")

if __name__ == "__main__":
    main()