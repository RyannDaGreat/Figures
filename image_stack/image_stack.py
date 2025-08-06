from rp import *

def create_motion_blur_image(
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
):
    video = resize_list(video, num_frames)  # 10 Frames
    video = resize_images_to_hold(video, height=frame_size, width=frame_size)

    ##############################################

    if total_shift_x is None: total_shift_x = total_shift
    if total_shift_y is None: total_shift_y = total_shift

    video = with_corner_radii(video, radius=10)
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


if __name__ == "__main__":
    # Example usage
    path = "/Users/ryan/Downloads/StillPepper.mp4"
    path = "/Users/ryan/Desktop/Screenshots/Screen Recording 2025-05-16 at 2.02.14 AM.mov"
    path = "/Users/ryan/Desktop/Screenshots/Screen Recording 2024-11-13 at 3.38.10 PM.mov"
    path = "/Users/ryan/Desktop/Screenshots/Screen Recording 2024-11-13 at 3.38.10 PM.mov"
    path = "/Users/ryan/Downloads/MakeTheBaloonsMove.mp4"

    video = load_video(path, use_cache=True)
    image = create_motion_blur_image(video,total_shift_y=100)

    import cv2
    background="blue"
    image=blend_images(background,image,)
    image=as_rgb_image(image,copy=False)
    image=as_byte_image(image,copy=False)
    image=cv_bgr_rgb_swap(image,copy=False)

    cv2.imshow("Display",image)
    cv2.waitKey(10)
