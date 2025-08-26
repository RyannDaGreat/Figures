import rp


def labeled_circle(text='8', color=(1, 0, 1, 1), rim_color=None, rim_width=-20, diameter=257, padding=10, font="Futura", text_color="black"):
    """
    Create a labeled circular graphic with customizable appearance.
    
    Args:
        text: Text to display in the center of the circle
        color: Fill color of the circle as RGBA tuple (default: magenta)
        rim_color: Color of the circle rim (defaults to same as fill color)
        rim_width: Width of the rim in pixels (negative for inward rim)
        diameter: Diameter of the circle in pixels
        padding: Padding around the circle in pixels
        font: Font family to use for the text
        text_color: Color of the text
    
    Returns:
        Image of the labeled circle
    """
    text = str(text)
    if rim_color is None:
        rim_color = color
    image_size = diameter + padding
    circle_image = rp.uniform_float_color_image(
        color="transparent", height=image_size, width=image_size
    )
    circle_image = rp.as_byte_image(circle_image)
    circle_image = rp.cv_draw_circle(
        circle_image,
        radius=diameter / 2,
        x=image_size / 2,
        y=image_size / 2,
        color=rim_color,
        rim=rim_width,
    )
    circle_image = rp.with_alpha_checkerboard(circle_image)
    text_image = rp.skia_text_to_image(
        text,
        font=font,
        size=diameter*.65,
        style=f"{text_color} bold",
        character_spacing=0,
    )
    text_image = rp.crop_image_zeros(text_image)
    circle_image = rp.skia_stamp_image(
        circle_image,
        text_image,
        sprite_origin="center",
        canvas_origin="center",
    )
    return circle_image