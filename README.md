# FigureSnippets Module

A Python module for creating various visual effects from images and videos.

## Submodules

### 🎬 Film Strip (`film_strip/`)
Create cinematic film strip effects from video sequences.

### ⭕ Labeled Circle (`labeled_circle/`)  
Generate customizable labeled circular graphics.

### 📸 Image Stack (`image_stack/`)
Create motion blur effects by stacking video frames with progressive transparency.

## Usage

```python
from FigureSnippets import film_strip, labeled_circle, create_motion_blur_image

# Create a film strip from video frames
strip = film_strip(video_frames, length=4)

# Generate a labeled circle
circle = labeled_circle(text="42", color=(1, 0, 1, 1))

# Create motion blur effect
blur_image = create_motion_blur_image(video_frames, num_frames=10)
```

## Interactive Demos

Each submodule includes a Marimo notebook for interactive exploration:

### Running the Notebooks

```bash
# Film Strip Demo
cd film_strip/
marimo run film_strip_demo.py

# Labeled Circle Demo  
cd labeled_circle/
marimo run labeled_circle_demo.py

# Image Stack Demo
cd image_stack/
marimo run image_stack_demo.py
```

**Note**: Notebooks must be run from their respective subdirectories for imports to work correctly.

### Demo Features

- **Interactive parameter controls** with sliders and dropdowns
- **Real-time preview** of visual effects
- **Preset buttons** for common configurations
- **Educational explanations** of how each effect works

## Requirements

- `rp` module (for image/video processing functions)
- `marimo` (for interactive notebooks)
- `numpy` 
- Standard Python libraries