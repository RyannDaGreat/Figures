import rp


def labeled_circle(text='8', color=(1, 0, 1, 1), rim_color=None, rim_width=-20, diameter=257, padding=10, font="Futura", text_color="black", font_size=None, text_style="bold", with_checkerboard=True, crop_zeros=True):
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
        font_size: Size of the text (defaults to diameter*.65)
        text_style: Style string like "bold", "italic", "bold italic" (combined with text_color)
        with_checkerboard: Whether to apply alpha checkerboard background
        crop_zeros: Whether to crop transparent/zero pixels from the text before placing it
    
    Returns:
        Image of the labeled circle
    """
    text = str(text)
    if rim_color is None:
        rim_color = color
    if font_size is None:
        font_size = diameter * 0.65
        
    image_size = diameter + padding
    circle_image = rp.uniform_float_color_image(
        color="transparent", height=image_size, width=image_size
    )
    circle_image = rp.as_byte_image(circle_image)
    
    # Draw circle with fill and rim in one call
    circle_image = rp.cv_draw_circle(
        circle_image,
        radius=diameter / 2,
        x=image_size / 2,
        y=image_size / 2,
        color=color,        # Fill color
        rim=rim_width,      # Rim thickness (positive=outward, negative=inward, 0=no rim)
        rim_color=rim_color,  # Rim color
        copy=False
    )
    if with_checkerboard:
        circle_image = rp.with_alpha_checkerboard(circle_image)
    
    # Combine text_color and text_style for the style string
    full_style = f"{text_color} {text_style}".strip()
    text_image = rp.skia_text_to_image(
        text,
        font=font,
        size=font_size,
        style=full_style,
        character_spacing=0,
    )
    if crop_zeros:
        text_image = rp.crop_image_zeros(text_image)
    circle_image = rp.skia_stamp_image(
        circle_image,
        text_image,
        sprite_origin="center",
        canvas_origin="center",
    )
    return circle_image