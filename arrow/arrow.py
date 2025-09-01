from rp import *
# ------------------------------------------------------------
# 1) Core: rp-native, composable Skia contour drawer (stroke-only)
# ------------------------------------------------------------
def skia_draw_contour(
    image,
    contour,
    *,
    # fill
    fill=None,                   # None | color | True (True => use stroke_color)
    fill_rule='winding',         # 'winding' | 'even-odd'
    # stroke
    stroke=True,
    stroke_color='white',
    stroke_width=1,
    stroke_type='solid',         # 'solid'|'dashed'|'dotted'|'dashdot'|'dashdotdot'
    stroke_dash=None,            # custom [on, off, ...] in px (overrides stroke_type)
    stroke_dash_scale=1.0,
    stroke_phase=0.0,
    stroke_cap='round',          # 'round'|'butt'|'square'
    stroke_join='miter',         # 'miter'|'round'|'bevel'
    stroke_miter_limit=10,
    stroke_align='center',       # Skia (python) exposes center-only stroking
    # shadow
    shadow=False,                # False|True|'fill'|'stroke'|'both'
    shadow_dx=0.0,
    shadow_dy=0.0,
    shadow_blur=10.0,
    shadow_color=(0, 0, 0, 1),
    shadow_opacity=1.0,
    shadow_only=False,
    # behavior
    antialias=True,
    close=True,
    copy=True,
):
    """
    Composable pipeline:
      normalize -> build path -> build paints/effects -> collect passes -> draw
    """
    import rp, numpy as np
    skia = rp.pip_import('skia')

    # ---------- validators ----------
    def _one_of(name, val, opts):
        if val not in opts:
            raise ValueError(f"{name}={val!r} not in {tuple(opts)}")
        return val

    fill_rule     = _one_of('fill_rule', fill_rule, ('winding', 'even-odd'))
    stroke_cap    = _one_of('stroke_cap', stroke_cap, ('round','butt','square'))
    stroke_join   = _one_of('stroke_join', stroke_join, ('miter','round','bevel'))
    stroke_type   = _one_of('stroke_type', stroke_type, ('solid','dashed','dotted','dashdot','dashdotdot'))
    stroke_align  = _one_of('stroke_align', stroke_align, ('center',))
    if shadow not in (False, True, 'fill', 'stroke', 'both'):
        raise ValueError("shadow must be False|True|'fill'|'stroke'|'both'")

    # ---------- stage 1: normalize image & path ----------
    img   = rp.as_rgba_image(rp.as_byte_image(image, copy=copy), copy=False)
    img   = np.ascontiguousarray(img)
    cnt   = rp.as_cv_contour(contour)
    if cnt.size == 0:
        return img

    pts   = [(float(x), float(y)) for (x, y) in cnt.reshape(-1, 2)]
    path  = skia.Path(); path.addPoly(pts, bool(close))
    path.setFillType({'winding': skia.PathFillType.kWinding,
                      'even-odd': skia.PathFillType.kEvenOdd}[fill_rule])

    # ---------- stage 2: builders ----------
    def _rgba_bytes(c_like):
        return rp.float_color_to_byte_color(rp.as_rgba_float_color(c_like))

    def build_fill_paint():
        if fill is None or fill is False:
            return None
        color = stroke_color if (fill is True) else fill
        return skia.Paint(
            AntiAlias=bool(antialias),
            Style=skia.Paint.kFill_Style,
            Color=skia.Color(*_rgba_bytes(color)),
        )

    def _dash_from_type(t, w):
        return {
            'solid'     : None,
            'dashed'    : [3.5*w, 2.5*w],
            'dotted'    : [1.0*w, 2.2*w],
            'dashdot'   : [6.0*w, 3.0*w, 1.0*w, 3.0*w],
            'dashdotdot': [6.0*w, 3.0*w, 1.0*w, 3.0*w, 1.0*w, 3.0*w],
        }[t]

    def build_path_effect():
        intervals = [float(v) for v in stroke_dash] if (stroke_dash is not None) \
                    else _dash_from_type(stroke_type, float(stroke_width))
        if intervals is None:
            return None
        intervals = [max(0.01, float(v))*float(stroke_dash_scale) for v in intervals]
        return skia.DashPathEffect.Make(intervals, float(stroke_phase))

    def build_stroke_paint():
        if not (stroke and stroke_width and stroke_width > 0):
            return None
        p = skia.Paint(
            AntiAlias=bool(antialias),
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=float(stroke_width),
            Color=skia.Color(*_rgba_bytes(stroke_color)),
        )
        p.setStrokeCap({'butt': skia.Paint.kButt_Cap,
                        'round': skia.Paint.kRound_Cap,
                        'square': skia.Paint.kSquare_Cap}[stroke_cap])
        p.setStrokeJoin({'miter': skia.Paint.kMiter_Join,
                         'round': skia.Paint.kRound_Join,
                         'bevel': skia.Paint.kBevel_Join}[stroke_join])
        p.setStrokeMiter(float(stroke_miter_limit))
        pe = build_path_effect()
        if pe is not None:
            p.setPathEffect(pe)
        return p

    def build_shadow_paint(base_paint):
        if not base_paint or not shadow:
            return None
        target = 'both' if shadow is True else str(shadow)
        sc = list(rp.as_rgba_float_color(shadow_color))
        sc[3] = max(0.0, min(1.0, sc[3]*float(shadow_opacity)))
        shadow_rgba = rp.float_color_to_byte_color(tuple(sc))
        filt = skia.ImageFilters.DropShadow(
            float(shadow_dx), float(shadow_dy),
            float(shadow_blur), float(shadow_blur),
            skia.Color(*shadow_rgba), None, None
        )
        q = skia.Paint(base_paint)
        q.setImageFilter(filt)
        q.setColor(skia.Color(*shadow_rgba))
        return (target, q)

    # ---------- stage 3: assemble passes ----------
    fill_paint   = build_fill_paint()
    stroke_paint = build_stroke_paint()

    passes = []  # list of (kind, paint)
    if shadow:
        res = build_shadow_paint(fill_paint)
        if res and res[0] in ('fill', 'both'):   passes.append(('path', res[1]))
        res = build_shadow_paint(stroke_paint)
        if res and res[0] in ('stroke', 'both'): passes.append(('path', res[1]))
        if shadow_only:  # only the shadow passes
            surface = skia.Surface(img)
            with surface as canvas:
                for _, paint in passes:
                    canvas.drawPath(path, paint)
            return img

    if fill_paint is not None:
        passes.append(('path', fill_paint))
    if stroke_paint is not None:
        passes.append(('path', stroke_paint))

    if not passes:
        return img

    # ---------- stage 4: draw ----------
    surface = skia.Surface(img)
    with surface as canvas:
        for _, paint in passes:
            canvas.drawPath(path, paint)

    return img


def skia_draw_contours(image, contours, **kwargs):
    """Plural form — cascades the same pipeline per contour; copy honored once."""
    import rp
    first = True
    out = image
    for cnt in contours:
        out = skia_draw_contour(out, cnt, copy=(kwargs.get('copy', True) if first else False), **kwargs)
        first = False
    if first and kwargs.get('copy', True):
        out = rp.as_rgba_image(rp.as_byte_image(out, copy=True), copy=False)
    return out


# ------------------------------------------------------------
# 2) Single "Grand Showcase" animation (one big video)
# ------------------------------------------------------------
def skia_grand_showcase_animation(
    out_path=None, width=1280, height=720, fps=30, seconds=12,
    bg='white', seed=0
):
    """
    Renders ONE big animation showcasing:
      - stroke presets (solid/dashed/dotted/dashdot/dashdotdot) + custom dash
      - animating stroke_phase
      - caps (butt/round/square) and joins (miter/round/bevel), miter limit
      - fill vs even-odd fill_rule
      - drifting drop shadow on fill/stroke/both
    Prefers MP4 (libx264). Falls back to GIF if x264 unavailable.
    Returns: path to output (str)
    """
    import math, os
    import numpy as np
    import rp
    # background (uint8 RGBA)
    rgba = rp.float_color_to_byte_color(rp.as_rgba_float_color(bg))
    H, W = int(height), int(width)
    base = np.empty((H, W, 4), np.uint8)
    base[..., 0] = rgba[0]; base[..., 1] = rgba[1]; base[..., 2] = rgba[2]; base[..., 3] = rgba[3]
    
    base=as_byte_image(as_rgba_image(linear_gradient_image(H,W,'instagram_sunset')))

    # ---- layout: 3 rows × 4 columns grid (12 showcases)
    rows, cols = 3, 4
    cell_w, cell_h = W // cols, H // rows
    def cell_center(r, c):
        return (c*cell_w + cell_w//2, r*cell_h + cell_h//2)

    # ---- contours
    def star(cx, cy, r1, r2, n=5):
        pts=[]
        for k in range(n*2):
            ang = (math.pi*k)/n - math.pi/2
            r = r1 if (k%2==0) else r2
            pts.append((cx + r*math.cos(ang), cy + r*math.sin(ang)))
        return np.asarray(pts, float)

    def jaggy(cx, cy, s):
        base=np.array([(60,0),(100,-30),(140,0),(120,40),(80,40)], float)
        return base*s + (cx-100, cy-10)

    def ring(cx, cy, Rout, Rin):
        outer = star(cx, cy, Rout, Rout*0.44)
        inner = star(cx, cy, Rin,  Rin*0.44)
        return np.vstack([outer, inner[::-1]])   # simple donut; even-odd punches a hole

    # Pre-build grid contours
    grid = []
    for r in range(rows):
        row=[]
        for c in range(cols):
            cx, cy = cell_center(r, c)
            if r == 0:
                row.append(star(cx, cy, cell_h*0.36, cell_h*0.16))
            elif r == 1:
                row.append(jaggy(cx, cy, s=cell_h/85.0))
            else:
                row.append(ring(cx, cy, Rout=int(cell_h*0.33), Rin=int(cell_h*0.17)))
        grid.append(row)

    # styling “programs” per cell (deterministic variety)
    stroke_types = ['solid','dashed','dotted','dashdot','dashdotdot']
    caps         = ['butt','round','square']
    joins        = ['miter','round','bevel']
    colorsA      = ['#1d4ed8','#be123c','#7e22ce','#0f766e','#a61e4d']  # blue, red, purple, teal, maroon
    colorsB      = ['black','midnightblue','indigo']

    def style_for_cell(r,c,t):
        # t in [0,1)
        if r == 0:
            st = stroke_types[c % len(stroke_types)]
            return dict(
                fill=None,
                stroke=True, stroke_color=colorsA[c%len(colorsA)], stroke_width=6 + (2 if st=='solid' else 0),
                stroke_type=st, stroke_phase= t*120.0 if st!='solid' else 0.0,
                stroke_cap='round', stroke_join='round',
                shadow='stroke', shadow_dx=4, shadow_dy=3, shadow_blur=6, shadow_opacity=0.5,
            )
        if r == 1:
            # joins showcase; caps cycle too
            join = joins[c % len(joins)]
            cap  = caps[(c+1) % len(caps)]
            return dict(
                fill=True,
                stroke=True, stroke_color=['#0b7285','#2b8a3e','#e8590c'][c%3], stroke_width=10,
                stroke_type='solid',
                stroke_cap=cap, stroke_join=join, stroke_miter_limit=10.0,
                shadow=True, shadow_dx=6, shadow_dy=6, shadow_blur=8, shadow_opacity=0.6,
            )
        if r == 2:
            # even-odd donuts with custom dashes; animate scale+phase and orbiting shadow
            dash=[16,8,3,8] if c%2==0 else [12,6]
            angle = t*2*math.pi + (c*2*math.pi/cols)
            dx, dy = 9*math.cos(angle), 9*math.sin(angle)
            return dict(
                fill='gold', fill_rule='even-odd',
                stroke=True, stroke_color=colorsB[c%len(colorsB)], stroke_width=8,
                stroke_dash=dash, stroke_dash_scale=1.0 + 0.25*math.sin(2*angle), stroke_phase=t*90.0,
                stroke_cap='square' if c%2 else 'round', stroke_join='round',
                shadow='both', shadow_dx=dx, shadow_dy=dy, shadow_blur=10, shadow_opacity=0.55,
            )
        return dict(fill=None, stroke=True, stroke_color='black', stroke_width=6)

    # ---- writer (MP4 preferred; GIF fallback) ----
    if out_path is None or str(out_path).strip()=="":
        out_path = "skia_grand_showcase.mp4"

    writer = None
    use_gif = False
    try:
        import imageio.v3 as iio
        writer = iio.get_writer(out_path, fps=fps, codec='libx264', quality=7, macro_block_size=1)
    except Exception:
        use_gif = True
        out_path = os.path.splitext(out_path)[0] + ".gif"
        frames = []

    # ---- render frames ----
    N = int(max(1, fps*seconds))
    for f in eta(range(N)):
        t = f / float(N)  # 0..1
        frame = base.copy()
        for r in range(rows):
            for c in range(cols):
                cnt = grid[r][c]
                style = style_for_cell(r,c,t)
                frame = skia_draw_contour(frame, cnt, copy=False, **style)
        if not use_gif:
            try:
                import imageio.v3 as iio
                writer.append_data(frame)
            except Exception:
                # switch to GIF on failure mid-run
                try: writer.close()
                except Exception: pass
                use_gif = True
                out_path = os.path.splitext(out_path)[0] + ".gif"
                frames = [frame]
        else:
            frames.append(frame)

    if not use_gif:
        writer.close()
        return out_path

    # GIF fallback
    from PIL import Image
    return save_video_mp4(frames)
    pil_frames=[Image.fromarray(f, 'RGBA') for f in frames]
    pil_frames[0].save(out_path, save_all=True, append_images=pil_frames[1:],
                       loop=0, duration=int(1000/max(1, fps)))
    return out_path










def _arrow_contours(x0,y0,x1,y1,tip_width=15,tip_height=15,tip_dimple=5, end_width=5, start_width=3):
    trail = [[x0,y0],[x1,y1]]

    dx=x1-x0
    dy=y1-y0

    mag = (dx**2+dy**2)**.5
    
    #Normalized Deltas
    ndx = dx / mag
    ndy = dy / mag
    
    #Normalized Right Vector
    nrx = -ndy
    nry = ndx
    
    tip_xl = x1 - nrx * tip_width - ndx * tip_height
    tip_yl = y1 - nry * tip_width - ndy * tip_height

    tip_xdimp = x1 - ndx * (tip_height - tip_dimple)
    tip_ydimp = y1 - ndy * (tip_height - tip_dimple)
    
    tip_xr = x1 + nrx * tip_width - ndx * tip_height
    tip_yr = y1 + nry * tip_width - ndy * tip_height
    
    tip = [[tip_xl,tip_yl],[x1,y1],[tip_xr,tip_yr],[tip_xdimp, tip_ydimp]]
    
    stem= [[x0,y0],[tip_xdimp,tip_ydimp]]

    

    full = [
        [
            tip_xdimp + end_width * -nrx / 2,
            tip_ydimp + end_width * -nry / 2,
        ],
        [
            x0 + start_width * -nrx / 2,
            y0 + start_width * -nry / 2,
        ],
        [
            x0 + start_width *  nrx / 2,
            y0 + start_width *  nry / 2,
        ],
        [
            tip_xdimp + end_width * +nrx / 2,
            tip_ydimp + end_width * +nry / 2,
        ],
        [tip_xr,tip_yr],
        [x1,y1],
        [tip_xl,tip_yl],
    ]
    return gather_vars('tip stem full')

def skia_draw_arrow(image, x0, y0, x1, y1, tip_width=15, tip_height=15, tip_dimple=5, end_width=5, start_width=3, color='black', **skia_kwargs):
    arrow = gather_args_call(_arrow_contours)
    
    skia_kwargs = dict(fill='translucent blue',shadow_opacity=1,shadow_color=(0,0,0,1),shadow_blur=2,stroke_width=1,
                       ) | skia_kwargs

    # image = skia_draw_contours(image,[arrow.stem,arrow.tip],**skia_kwargs)
    image = skia_draw_contour(image, arrow.full, **skia_kwargs)
    # image = skia_draw_contours(image,[dilated_contour(arrow.tip,r,loop=True) for r in [5] ],**skia_kwargs)
    return image



def draw(image, points):
    h, w = get_image_dimensions(image)
    box = [[0, 0], [w, 0], [w, h], [0, h], [0, 0]]

    box = as_numpy_array(box)
    points = as_numpy_array(points)
    xs, ys = as_numpy_array(points.T)

    image = cv_draw_contour(image, box, color="black")
    # image = cv_draw_arrow(image, *list_flatten(points), color="black", tip_length=0.1)
    image = skia_draw_arrow(image, *list_flatten(points), color="black")
    image = cv_draw_circles(image, xs, ys, rim=1)
    image = cv_draw_circle(image, w / 2, h / 2, rim=1)
    return image


def video_demo():
    video = []
    h, w = 400, 200
    gradient = [as_rgba_float_color("light random") for _ in range(50)]
    for a in eta(range(360)):
        points = rp.r._gradient_angle_to_points(h, w, a)
        image = linear_gradient_image(
            h,
            w,
            # gradient_presets.electric_rainbow,
            gradient,
            direction=a,
        )
        image = draw(image, points)
        image = labeled_image(image, "{0}°".format(a), font="Futura")
        video.append(image)
    return video


#video = video_demo()
#display_video(video, loop=True)
# video_path = save_video_mp4(video, "gradient_angles.mp4")
# open_file_with_default_application(video_path)
