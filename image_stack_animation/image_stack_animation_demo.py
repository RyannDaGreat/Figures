#!/usr/bin/env python3
"""
Image Stack Animation Demo - Creates an animated GIF showing image stack parameter transitions
"""

import sys
import os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from image_stack import create_image_stack
import rp

def create_image_stack_animation():
    """Create animated image stack sequence with interpolated parameters"""
    
    def lerp(a, b, t):
        """Linear interpolation between a and b"""
        return a + (b - a) * t
    
    def smooth_step(t):
        """Smooth interpolation curve"""
        return t * t * (3 - 2 * t)
    
    # Animation settings
    frames = 80
    canvas_size = 400
    
    # Load or create sample video frames
    try:
        video = rp.load_video("/Users/ryan/Downloads/StillPepper.mp4", use_cache=True)
    except:
        # Create synthetic video frames if real video unavailable
        video = []
        for i in range(20):
            # Create colorful gradient frames
            angle = i * 18  # 360/20 degrees per frame
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
        # Keyframe 0: Standard stack
        {
            'num_frames': 8,
            'total_shift_x': 150,
            'total_shift_y': 150,
            'frame_size': 200,
            'shadow_shift': 8,
            'shadow_blur': 20,
            'shadow_opacity': 0.3,
            'alphas_exponent': 0.6,
            'shadow_color': '#000000'
        },
        
        # Keyframe 1: More frames, tight spacing
        {
            'num_frames': 15,
            'total_shift_x': 80,
            'total_shift_y': 80,
            'frame_size': 180,
            'shadow_shift': 4,
            'shadow_blur': 15,
            'shadow_opacity': 0.4,
            'alphas_exponent': 0.3,
            'shadow_color': '#333333'
        },
        
        # Keyframe 2: Wide spread, fewer frames
        {
            'num_frames': 5,
            'total_shift_x': 300,
            'total_shift_y': 100,
            'frame_size': 240,
            'shadow_shift': 15,
            'shadow_blur': 35,
            'shadow_opacity': 0.5,
            'alphas_exponent': 0.8,
            'shadow_color': '#FF0000'
        },
        
        # Keyframe 3: Vertical stack
        {
            'num_frames': 10,
            'total_shift_x': 50,
            'total_shift_y': 250,
            'frame_size': 160,
            'shadow_shift': 20,
            'shadow_blur': 25,
            'shadow_opacity': 0.2,
            'alphas_exponent': 0.4,
            'shadow_color': '#0000FF'
        },
        
        # Keyframe 4: Diagonal spread
        {
            'num_frames': 12,
            'total_shift_x': 200,
            'total_shift_y': 200,
            'frame_size': 220,
            'shadow_shift': 6,
            'shadow_blur': 40,
            'shadow_opacity': 0.6,
            'alphas_exponent': 0.9,
            'shadow_color': '#00FF00'
        },
        
        # Keyframe 5: Horizontal spread
        {
            'num_frames': 8,
            'total_shift_x': 280,
            'total_shift_y': 40,
            'frame_size': 190,
            'shadow_shift': 12,
            'shadow_blur': 18,
            'shadow_opacity': 0.35,
            'alphas_exponent': 0.5,
            'shadow_color': '#FF00FF'
        },
        
        # Keyframe 6: No shadows, tight pack
        {
            'num_frames': 6,
            'total_shift_x': 60,
            'total_shift_y': 60,
            'frame_size': 250,
            'shadow_shift': 0,
            'shadow_blur': 0,
            'shadow_opacity': 0.0,
            'alphas_exponent': 0.7,
            'shadow_color': '#000000'
        },
        
        # Keyframe 7: Heavy shadows, spread out
        {
            'num_frames': 9,
            'total_shift_x': 180,
            'total_shift_y': 180,
            'frame_size': 170,
            'shadow_shift': 25,
            'shadow_blur': 50,
            'shadow_opacity': 0.7,
            'alphas_exponent': 0.2,
            'shadow_color': '#800080'
        },
        
        # Keyframe 8: Back to start-like
        {
            'num_frames': 10,
            'total_shift_x': 120,
            'total_shift_y': 120,
            'frame_size': 210,
            'shadow_shift': 10,
            'shadow_blur': 22,
            'shadow_opacity': 0.25,
            'alphas_exponent': 0.55,
            'shadow_color': '#000000'
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
            
            # Interpolate numeric parameters
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
        
        # Create image stack with current parameters
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
            
            # Blend with blue background and add checkerboard
            final_result = rp.blend_images("#0000FF", result)
            final_result = rp.with_alpha_checkerboard(final_result)
            final_result = rp.as_byte_image(final_result, copy=False)
            
            # Resize to consistent canvas size
            final_result = rp.resize_image_to_fit(final_result, canvas_size, canvas_size)
            final_result = rp.as_rgba_image(final_result, copy=False)
            
            animation_frames.append(final_result)
            
        except Exception as e:
            print(f"Error creating frame {frame_idx}: {e}")
            # Create a blank frame if error
            blank = rp.as_rgba_image(rp.uniform_float_color_image(canvas_size, canvas_size, 'white'), copy=False)
            animation_frames.append(blank)
        
        if frame_idx % 10 == 0:
            print(f"Generated image stack frame {frame_idx + 1}/{frames}")
    
    return animation_frames

if __name__ == "__main__":
    print("Creating image stack animation...")
    frames = create_image_stack_animation()
    
    # Save as animated GIF
    output_path = '../assets/image_stack_animation.gif'
    rp.save_animated_gif(frames, output_path)
    print(f"Image stack animation saved to: {output_path}")
    
    # Display a sample frame
    if frames:
        rp.display_image(frames[len(frames) // 2])