"""
FigureSnippets - Image and video processing utilities for creating visual effects.

This module provides functions for creating various visual effects:
- film_strip: Create film strip effects from video sequences
- labeled_circle: Generate labeled circular graphics
- create_motion_blur_image: Create motion blur effects from videos
"""

from .film_strip import film_strip
from .labeled_circle import labeled_circle
from .image_stack import create_motion_blur_image

__all__ = ['film_strip', 'labeled_circle', 'create_motion_blur_image']