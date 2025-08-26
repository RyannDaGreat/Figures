def labeled_circle(text='8',color=(1, 0, 1, 1), rim_color=None, rim_width=-20, diameter=257, padding=10, font="Futura", text_color="black"):
    # 2025-08-26 01:56:04.661988
    text=str(text)
    if rim_color is None:
        rim_color = color
    image_size = diameter + padding
    circle_image = rp.uniform_float_color_image(
        color="transparent", height=image_size, width=image_size
    )
    circle_image = rp.as_byte_image(circle_image)
    # circle_image=as_rgb_image(circle_image)
    circle_image = rp.cv_draw_circle(
        circle_image,
        radius=diameter / 2,
        x=image_size / 2,
        y=image_size / 2,
        color=rim_color,
        rim=rim_width,
    )
    circle_image = rp.with_alpha_checkerboard(circle_image)
    text_image = skia_text_to_image(
        text,
        font=font,
        size=diameter*.65,
        style=f"{text_color} bold",
        character_spacing=0,
    )
    text_image = crop_image_zeros(text_image)
    circle_image = skia_stamp_image(
        circle_image,
        text_image,
        sprite_origin="center",
        canvas_origin="center",
    )
    display_alpha_image(circle_image)
display_alpha_image(labeled_circle(14))