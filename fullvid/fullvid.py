import rp
from rp.r import _omni_load
from rp.git.Figures.labeled_circle import labeled_circle
from rp.git.Figures.arrow.arrow import (
    # skia_draw_contour,
    skia_draw_contours,
    skia_draw_arrow,
)

edit_path = "/Users/ryan/CleanCode/Projects/Google2025_Paper/inferblobs_edit_results/[Seed 5176] Judge_ Walk Out_copy2"
edit_path = "/Users/ryan/CleanCode/Projects/Google2025_Paper/inferblobs_edit_results/[Seed 6303] Sora Basketball_ The ball goes into the hoop_copy1" ; indices = [3, 5]
edit_path = "/Users/ryan/CleanCode/Projects/Google2025_Paper/inferblobs_edit_results/[Seed 1515] Blacks Freeze Camera_copy2" ; indices = slice(None)

hand_icon_path = "https://github.com/RyannDaGreat/MacCursors/blob/main/src/png/handopen%402x.png?raw=True"
grab_icon_path = "https://github.com/RyannDaGreat/MacCursors/blob/main/src/png/handgrabbing@2x.png?raw=true"

hand_icon = rp.load_image(hand_icon_path, use_cache=True)
grab_icon = rp.load_image(grab_icon_path, use_cache=True)

counter_video_path    = rp.path_join(edit_path, "counter_video.mp4")
target_video_path     = rp.path_join(edit_path, "output_video.mp4")
counter_tracks_path   = rp.path_join(edit_path, "counter_tracks.pth")
target_tracks_path    = rp.path_join(edit_path, "target_tracks.pth")
target_visibles_path  = rp.path_join(edit_path, "target_visibles.pth")
counter_visibles_path = rp.path_join(edit_path, "counter_visibles.pth")

target_video     = rp.load_video(target_video_path,  use_cache=True)
counter_video    = rp.load_video(counter_video_path, use_cache=True)
target_tracks    = rp.as_numpy_array(_omni_load(target_tracks_path))
counter_tracks   = rp.as_numpy_array(_omni_load(counter_tracks_path))
target_visibles  = rp.as_numpy_array(_omni_load(target_visibles_path))
counter_visibles = rp.as_numpy_array(_omni_load(counter_visibles_path))

target_tracks    = target_tracks   [:, indices]
counter_tracks   = counter_tracks  [:, indices]
target_visibles  = target_visibles [:, indices]
counter_visibles = counter_visibles[:, indices]

N, T, H, W = rp.validate_tensor_shapes(
    counter_video    = "numpy: T H W RGB",
    target_video     = "numpy: T H W RGB",
    counter_tracks   = "numpy: T N XY",
    target_tracks    = "numpy: T N XY",
    counter_visibles = "numpy: T N",
    target_visibles  = "numpy: T N",
    XY  = 2,
    RGB = 3,
    H   = 480,
    W   = 720,
    return_dims="N T H W",
)

colors = [
    (*rp.hsv_to_rgb_float_color(h, 0.5, 1), 1)
    for h in rp.np.linspace(0, 1, num=N, endpoint=False)
]
# display_image(tiled_images(uniform_float_color_image(256,256,color) for color in colors))

circles = [
    rp.with_drop_shadow(
        labeled_circle(
            text=str(n + 1),
            color=color,
            rim_color="black",
            diameter=30,
            rim_width=2,
            padding=30,
            with_checkerboard=False,
        ),
        color="white",
        opacity=0.5,
    )
    for n,color in enumerate(colors)
]
circles=rp.cv_resize_images(circles,size=.75)
#display_alpha_image(blend_images('dark translucent blue',tiled_images(circles)))

@rp.memoized_lru
def get_circles_layer(tracks, visibles, frame_number, track_numbers=None):
    """
    EXAMPLE:
        >>> f=[get_circles_layer(target_tracks,target_visibles,t) for t in eta(range(T))]
        >>> q=skia_stamp_video(target_video,f)
        >>> display_video(q)
    """

    if track_numbers is None: track_numbers=range(N)
    layer = rp.uniform_byte_color_image(H, W)
    
    for n in track_numbers:
        circle=circles[n]
        x,y=tracks[frame_number,n]
        v=visibles[frame_number,n]
        if v:
            layer = rp.skia_stamp_image(layer,circle,offset=[x,y], sprite_origin=[.5,.5],copy=False)
                
    return layer

@rp.memoized_lru
def get_hand_layer(tracks, visibles, frame_number, grabbing=False, dx=0, dy=0, hand_size=1.0, track_numbers=None):
    """
    EXAMPLE:
        >>> f=[get_circles_layer(target_tracks,target_visibles,t) for t in eta(range(T))]
        >>> q=skia_stamp_video(target_video,f)
        >>> display_video(q)
    """

    if track_numbers is None: track_numbers=range(N)
    layer = rp.uniform_byte_color_image(H, W)
    
    for n in track_numbers:
        x,y=tracks[frame_number,n]
        v=visibles[frame_number,n]
        hand = grab_icon if grabbing else hand_icon
        hand = rp.cv_resize_image(hand, hand_size)
        if v:
            layer = rp.skia_stamp_image(layer,hand,offset=[x+dx,y+dy], sprite_origin=[.5,.5],copy=False)
                
    return layer

@rp.memoized_lru
def get_trails_layer(tracks, visibles, frame_number, track_numbers=None):

    if track_numbers is None: track_numbers=range(N)
    layer = rp.uniform_byte_color_image(H, W)
    
    if frame_number>0:

        for n in track_numbers:
            color=colors[n]
            
            old_vis=False
            subtrails = []
            for t in range(frame_number+1):
                vis = visibles[t, n]
                xy  = tracks[t,n]
                if vis and not old_vis:
                    subtrails+=[[xy]]
                elif vis and old_vis:
                    subtrails[-1]+=[xy]
                old_vis = vis
                
            layer = skia_draw_contours(
                layer,
                subtrails,
                #
                stroke_width=4,
                shadow_opacity=1,
                shadow_color=(1, 1, 1, 1),
                shadow_blur=5,
                stroke_join='round',
                stroke_type='dotted',
                stroke_dash_scale=.5,
                fill=None,
                stroke_color=color,
                close=False,
            )
            
    layer=rp.with_drop_shadow(layer,color='black',blur=10)

    return layer

@rp.memoized_lru
def get_arrows_layer(src_tracks,src_visibles,dst_tracks,dst_visibles,frame_number,track_numbers=None,circle_radius=12):
    if track_numbers is None: track_numbers=range(N)
    layer = rp.uniform_byte_color_image(H, W)
    
    for n in track_numbers:
        color=colors[n]
        
        color_b = rp.with_color_brightness(color,.8)
        color_b = rp.with_color_saturation(color,.8)

        src_v = src_visibles[frame_number,n]
        dst_v = dst_visibles[frame_number,n]
        src_xy = src_tracks[frame_number,n]
        dst_xy = dst_tracks[frame_number,n]
        
        delta = dst_xy - src_xy
        delta_mag = rp.magnitude(delta)
        delta_norm = delta / delta_mag
        
        # src_xy = src_xy + delta_norm * circle_radius
        dst_xy = dst_xy - delta_norm * circle_radius
        
        v = src_v and dst_v and delta_mag > 2 * circle_radius
        dst_x, dst_y = dst_xy
        src_x, src_y = src_xy
        
        
        if v:
            layer = skia_draw_arrow(
                layer,
                src_x,
                src_y,
                dst_x,
                dst_y,
                copy=False,
                fill=color,
                stroke_color=color_b,
                stroke_join="round",
            )


    layer=rp.with_drop_shadow(layer,color='black',blur=20)
        
    return layer

@rp.memoized_lru
def get_status_layer(text, color='translucent green', width=200, offset=20, x_shift=0):
    background = rp.uniform_byte_color_image(height=60,width=width,color=color)
    background = rp.with_corner_radius(background, 40, antialias=False)
    background = rp.with_alpha_outline(background, inner_radius=10, color=' translucent white ')
    text_image = rp.skia_text_to_image(text, font="Futura", size=50, color='white')
    label_image = rp.skia_stamp_image(background,text_image,sprite_origin=(.5,.5),canvas_origin=(.5,.5))
    label_image = rp.cv_resize_image(label_image,.5,alpha_weighted=True)
    label_image = rp.bordered_image_solid_color(label_image, thickness=round(offset), color='transparent')
    label_image = rp.shift_image(label_image, x=x_shift)
    return label_image

@rp.memoized_lru
def get_chat_layer(text='Hello World', background_color='black', rim_color='gray', text_color='white', width=400, height=60, font_size=24, y_offset=-20):
    background = rp.uniform_byte_color_image(height=height, width=width, color=background_color)
    background = rp.with_corner_radius(background, 20, antialias=False)
    background = rp.with_alpha_outline(background, inner_radius=10, color=rim_color)
    text_image = rp.skia_text_to_image(text, font="Futura", size=font_size, color=text_color)
    chat_image = rp.skia_stamp_image(background, text_image, sprite_origin=(.5,.5), canvas_origin=(.5,.5))
    chat_image = rp.cv_resize_image(chat_image,.5,alpha_weighted=True)
    
    # Position at bottom-center with y_offset
    layer = rp.uniform_byte_color_image(H, W)
    layer = rp.skia_stamp_image(layer, chat_image, offset=[0, y_offset], sprite_origin=(.5, 1), canvas_origin=(.5, 1), copy=False)
    
    return layer

def srgb_blend(x,y,a):
    x = rp.srgb_to_linear(x)
    y = rp.srgb_to_linear(y)
    z = rp.blend_images(x, y, a)
    z = rp.linear_to_srgb(z)
    return z

@rp.memoized_lru
def blended_video_layer(frame_number, alpha):
    return srgb_blend(counter_video[frame_number], target_video[frame_number], alpha)

@rp.memoized_lru
def final_frame(
    frame_number=25,
    video_alpha=.5,
    track_alpha=1,
    circles_alpha=1,
    arrows_alpha=1,
    target_trails_alpha=1,
    counter_trails_alpha=1,
    blended_trails_alpha=1,
    hand_alpha=1,
    hand_grabbing=False,
    hand_dx=0,
    hand_dy=0,
    hand_size=1.0,
    track_numbers=None,
    status_text = "Input Video",
    status_color = "translucent green",
    status_width = 200,
    status_offset = 30,
    status_alpha = 1,
    status_x_shift = 0,
    chat_alpha = 1,
    chat_text = "Hello World",
    chat_background_color = "black",
    chat_rim_color = "gray",
    chat_text_color = "white",
    chat_width = 400,
    chat_height = 60,
    chat_font_size = 24,
    chat_y_offset = -20,
):

    blended_tracks = rp.blend(counter_tracks, target_tracks, track_alpha)
    visibles = counter_visibles & target_visibles

    blended_frame = blended_video_layer(frame_number, video_alpha)

    circles_layer = get_circles_layer(blended_tracks, visibles, frame_number, track_numbers)
    arrows_layer = get_arrows_layer(counter_tracks, counter_visibles, blended_tracks, target_visibles, frame_number, track_numbers)
    target_trails_layer  = get_trails_layer(target_tracks , target_visibles , frame_number, track_numbers)
    counter_trails_layer = get_trails_layer(counter_tracks, counter_visibles, frame_number, track_numbers)
    blended_trails_layer = get_trails_layer(blended_tracks, counter_visibles, frame_number, track_numbers)
    hand_layer = get_hand_layer(blended_tracks, visibles, frame_number, hand_grabbing, hand_dx, hand_dy, hand_size, track_numbers)
    status_layer = get_status_layer(status_text, status_color, status_width, status_offset, status_x_shift)
    chat_layer = get_chat_layer(chat_text, chat_background_color, chat_rim_color, chat_text_color, chat_width, chat_height, chat_font_size, chat_y_offset)

    output = blended_frame
    
    def imblend(x,y,a):return srgb_blend(x,y,a)
    # def imblend(x,y,a):return rp.skia_stamp_image(x,y,alpha=a)

    output = imblend(output, target_trails_layer , target_trails_alpha )
    output = imblend(output, blended_trails_layer, blended_trails_alpha)
    output = imblend(output, counter_trails_layer, counter_trails_alpha)
    output = imblend(output, circles_layer,circles_alpha)
    output = imblend(output, arrows_layer, arrows_alpha)
    output = imblend(output, hand_layer, hand_alpha)
    output = imblend(output, chat_layer, chat_alpha)
    output = imblend(output, status_layer, status_alpha)

    return output

    
    
