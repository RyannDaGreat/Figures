#!/usr/bin/env python3
import sys
import math
sys.path.insert(0, '/opt/homebrew/lib/python3.10/site-packages/rp/git/Figures')

from arrow import skia_draw_arrow
import rp
import numpy as np

def lerp(a, b, t):
    """Linear interpolation between a and b"""
    return a + (b - a) * t

def smooth_step(t):
    """Smooth interpolation curve"""
    return t * t * (3 - 2 * t)

def create_arrow_animation():
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
        print(f"Generated frame {frame_idx + 1}/{frames}")
    
    return animation_frames

# Generate animation
print("Creating arrow animation...")
frames = create_arrow_animation()

# Save as animated GIF
output_path = '/opt/homebrew/lib/python3.10/site-packages/rp/git/Figures/assets/arrow_animation.gif'
rp.save_animated_gif(frames, output_path)
print(f"Arrow animation saved to: {output_path}")