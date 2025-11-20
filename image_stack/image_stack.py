from rp import *

def create_image_stack(
    video,
    num_frames=10,
    total_shift=200,
    total_shift_x=None,
    total_shift_y=None,
    frame_size=256,
    shadow_shift=10,
    shadow_blur=30,
    shadow_color="black",
    shadow_opacity=0.25,
    alphas_exponent=0.5,
    corner_radius=10,
):
    video = resize_list(video, num_frames)  # 10 Frames
    video = resize_images_to_hold(video, height=frame_size, width=frame_size)

    ##############################################

    if total_shift_x is None: total_shift_x = total_shift
    if total_shift_y is None: total_shift_y = total_shift

    video = with_corner_radii(video, radius=corner_radius)
    video = bordered_images_solid_color(video, color="transparent", thickness=30)
    video = with_drop_shadows(
        video,
        x=shadow_shift,
        y=shadow_shift,
        color=shadow_color,
        blur=shadow_blur,
        opacity=shadow_opacity,
    )
    video = [
        shift_image(
            f,
            x=i * total_shift_x / num_frames,
            y=i * total_shift_y / num_frames,
        )
        for i, f in enumerate(video)
    ]
    video = crop_images_to_max_size(video)

    image = np.zeros_like(video[0])
    alphas = np.linspace(0, 1, num_frames, endpoint=False)
    alphas = alphas**alphas_exponent
    # Higher exponent -> sharper dropoff, lower exponent -> see more frames

    for frame, alpha in eta(zip(video[::-1], alphas), length=num_frames):
        image = with_alpha_channel(image, get_alpha_channel(image) * alpha)
        image = blend_images(image, frame)

    return image


