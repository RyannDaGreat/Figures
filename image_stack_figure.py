from rp import *

num_frames = 10
shift = 200
path = "/Users/ryan/Downloads/StillPepper.mp4"
shadow_shift = 5
background='white'

video = load_video(path, use_cache=True)
video = resize_list(video, num_frames)  # 10 Frames
video = crop_images_to_square(video)
video = resize_images(video, size=(256, 256))

video=with_corner_radii(video,radius=10)
video = bordered_images_solid_color(video, color="transparent", thickness=30)
video = with_drop_shadows(
    video,
    x=shadow_shift,
    y=shadow_shift,
    color="black",
    blur=30,
    opacity=.5,
)
video = [
        shift_image(
            f,
            i * shift / num_frames,
            i * shift / num_frames,
        )
        for i, f in enumerate(video)
    ]
video=crop_images_to_max_size(video)
video = [
    blend_images(f, background, a)
    for f, a in zip(video, np.linspace(0, 1, num_frames, endpoint=False))
]
# video=[blend_images(1,x) for x in video]

image=overlay_images(video[::-1])

# display_alpha_image(image)
display_image(blend_images(background, image))
# display_image(image)
# display_image(get_alpha_channel(image))

save_image(image, 'image_stack.png')
copy_image_to_clipboard(image)
