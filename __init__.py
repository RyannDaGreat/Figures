"""
FigureSnippets - Image and video processing utilities for creating visual effects.

This module provides functions for creating various visual effects:
- film_strip: Create film strip effects from video sequences
- labeled_circle: Generate labeled circular graphics
- create_image_stack: Create image stack effects from videos
"""

from .film_strip import film_strip
from .labeled_circle import labeled_circle
from .image_stack import create_image_stack

__all__ = ['film_strip', 'labeled_circle', 'create_image_stack']