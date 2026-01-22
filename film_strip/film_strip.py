from rp import *
from functools import partial


def film_strip(video, length=None, height=None, width=None, vertical=False, film_color='black'):
    """
    Create a film strip effect from a video sequence.
    
    Args:
        video: List of video frames/images
        length: Optional number of frames to use (defaults to all frames)
        height: Height to resize frames to (default: 480)
        width: Width to resize frames to (default: 720)
    
    Returns:
        Image with film strip effect applied
    """

    if vertical:
        video = rp.rotate_images(video, angle=-90)
        output = rp.gather_args_recursive_call(vertical=False)
        output = rp.rotate_image(output, 90)
        return output

    if height is None:height=get_video_height(video)
    if width is None:width=get_video_width(video)

    arrow = crop_image_zeros(skia_text_to_image("⮕", style="black"))
    down_arrow = rotate_image(arrow, 90)
    arr = partial(join_with_separator, separator=arrow)
    pad = partial(bordered_images_solid_color, color="transparent", height=20)
    rnd = partial(with_corner_radii, radius=20, antialias=False)
    otl = partial(with_alpha_outlines, outer_radius=20, allow_growth=True, color="gray")

    if length is not None:
        video = resize_list(video, length)
    video = resize_images(video, size=(height, width))
    video = rnd(video)
    video = otl(video)
    video = pad(video)

    strip = horizontally_concatenated_images(video)
    strip = blend_images(film_color, strip)

    alpha = get_alpha_channel(strip)

    film_dots = crop_image_zeros(
        skia_text_to_image("• " * 1000, style="black on white", font="Arial")
    )
    film_dots = crop_image(film_dots, height=32, origin="center")
    alpha = skia_stamp_image(
        alpha, film_dots, sprite_origin="top", canvas_origin="top"
    )
    alpha = skia_stamp_image(
        alpha, film_dots, sprite_origin="bottom", canvas_origin="bottom"
    )
    alpha = blend_images(alpha, get_image_alpha(strip), mode='multiply')

    strip = with_alpha_channel(strip, alpha)
    strip = with_corner_radius(strip, 20)

    strip = bordered_image_solid_color(strip, "transparent", thickness=40)

    return strip
