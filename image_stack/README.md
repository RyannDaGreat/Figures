# Image Stack Module

This module provides functionality for creating motion blur effects from video sequences, creating a stacked appearance where frames overlay with progressive transparency.

## Core Function

### `create_motion_blur_image()`

Creates a motion blur effect by stacking video frames with progressive transparency and spatial shifts.

**Parameters:**
- `video`: List of video frames/images
- `num_frames`: Number of frames to use (default: 10)
- `total_shift`: Total pixel shift for motion effect (default: 200)
- `total_shift_x`: Horizontal shift in pixels (defaults to `total_shift`)
- `total_shift_y`: Vertical shift in pixels (defaults to `total_shift`)
- `frame_size`: Size to resize frames to (default: 256)
- `shadow_shift`: Shadow offset in pixels (default: 10)
- `shadow_blur`: Shadow blur radius (default: 30)
- `shadow_color`: Shadow color (default: "black")
- `shadow_opacity`: Shadow transparency (default: 0.25)
- `alphas_exponent`: Controls fade curve - higher values = sharper dropoff (default: 0.5)

**Returns:** Composite image with motion blur effect

## Usage Example

```python
from rp import load_video
from FigureSnippets.image_stack import create_motion_blur_image

# Load video
video = load_video("path/to/video.mp4")

# Create motion blur effect
result = create_motion_blur_image(
    video,
    num_frames=15,
    total_shift_x=300,
    total_shift_y=150
)

# Display or save result
display_image(result)
```

## Interactive Streamlit App

This module includes a web-based interface for interactive parameter adjustment.

### Running the Streamlit App

```bash
cd /path/to/FigureSnippets/image_stack
streamlit run image_stack_streamlit.py
```

### App Features

- **Video Loading**: Load videos from file paths or URLs
- **Real-time Parameter Adjustment**: Interactive sliders for all motion blur parameters
- **Live Preview**: See changes immediately
- **Export Options**: Save generated images
- **Responsive Interface**: Works on desktop and mobile

### App Controls

- **Motion Parameters**: Adjust frame count, shift amounts, and frame size
- **Shadow Settings**: Control shadow appearance and positioning  
- **Color Controls**: Pick shadow and background colors
- **Generation**: Click "Update Image" to apply changes

The Streamlit app provides an intuitive way to experiment with different motion blur effects and find the perfect settings for your videos.