from rp import *

arrow = crop_image_zeros(skia_text_to_image("⮕", style="black"))


def film_strip(video, length=None, height=480, width=720):
    down_arrow = rotate_image(arrow, 90)
    arr = partial(join_with_separator, separator=arrow)
    pad = partial(bordered_images_solid_color, color="transparent", height=20)
    rnd = partial(with_corner_radii, radius=20, antialias=False)
    otl = partial(with_alpha_outlines, outer_radius=20, allow_growth=True, color="gray")

    if length is not None:
        video = resize_list(video, length)
    video = resize_images(video, size=(480, 720))
    video = rnd(video)
    video = otl(video)
    video = pad(video)

    strip = horizontally_concatenated_images(video)
    strip = blend_images("black", strip)

    alpha = get_alpha_channel(strip)

    film_dots = crop_image_zeros(
        skia_text_to_image("• " * 100, style="black on white", font="Arial")
    )
    film_dots = crop_image(film_dots, height=32, origin="center")
    alpha = skia_stamp_image(
        alpha, film_dots, sprite_origin="top ", canvas_origin="top "
    )
    alpha = skia_stamp_image(
        alpha, film_dots, sprite_origin="bottom ", canvas_origin="bottom "
    )

    strip = with_alpha_channel(strip, alpha)
    strip = with_corner_radius(strip, 20)

    strip = bordered_image_solid_color(strip, "transparent", thickness=40)
    # strip=with_drop_shadow(strip,x=10,y=10,opacity=.5,blur=20)
    #
    # strip=with_alpha_checkerboard(strip)

    return strip


src_path = "/Users/ryan/CleanCode/Projects/Google2025_Paper/UserStudy/video_pairs/ATI_0181--[Seed 4849] AUTOTEST_ 00877.mp4.mp4"
src_path = "/Users/ryan/CleanCode/Projects/Google2025_Paper/UserStudy/video_pairs/ATI_0259--[Seed 5459] AUTOTEST_ 00940.mp4.mp4"
video_paths = [
    "/Users/ryan/CleanCode/Projects/Google2025_Paper/inferblobs_edit_results/[Seed 168] Judge_ Walk Out/counter_video.mp4",
    "/Users/ryan/CleanCode/Projects/Google2025_Paper/inferblobs_edit_results/[Seed 168] Judge_ Walk Out/counter_tracking_frames.mp4",
    "/Users/ryan/CleanCode/Projects/Google2025_Paper/inferblobs_edit_results/[Seed 168] Judge_ Walk Out/tracking_frames.mp4",
    "/Users/ryan/CleanCode/Projects/Google2025_Paper/inferblobs_edit_results/[Seed 168] Judge_ Walk Out/output_video.mp4",
]
videos = load_videos(video_paths)


video = load_video(src_path, use_cache=True)
video = video[:, -480:]
invid, ours, ati, target = split_tensor_into_regions(video, 1, 1, 4)
wholevid = np.concatenate([invid[::-1], target])

L = 7
wholevid = resize_list(wholevid, L)

figure = crop_image_zeros(
    with_drop_shadow(
        vertically_concatenated_images(
            join_with_separator(
                [film_strip(x, length=4) for x in videos],
                uniform_float_color_image(height=10,width=0),
            )
        ),
        x=10,
        y=10,
        blur=30,
        opacity=0.5,
    )
)


copy_image_to_clipboard(figure)
display_alpha_image(figure)
# whole_strip=film_strip(wholevid)
# display_alpha_image(whole_strip)
#
#
# vertically_concatenated_images
