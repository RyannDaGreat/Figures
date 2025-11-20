pdf_path='/Users/ryan/CleanCode/Projects/Google2025_Paper/MotionV2V- Editing Motion in a Video.pdf'
pdf_path=download_to_cache('https://arxiv.org/pdf/2501.08331') #GWTF
dpi = 50
images=r._load_images_via_pdf2image(pdf_path,dpi=dpi,use_cache=True)
images=images[:8]#Page Selection
h,w=get_video_dimensions(images)
h_ratio=1.5 #1 is perfect pivot at middle bottom. Larger fans out more. Less than 1 self overlaps. .5 pivots at center of page. 0 is invalid.
up_images=images
up_images=as_rgba_images(up_images)
up_images=crop_images(up_images,height=round(h*h_ratio)*2,origin='top')
#up_images=[blend_images('transparent white',image) for image in up_images]
angle=45
n=len(images)
angles=np.linspace(-angle,angle,num=n,endpoint=True)
feather_images=rotate_images(up_images,angle=angles)
feather_images=crop_images_to_max_size(feather_images,origin='center')
fh,fw=get_video_dimensions(feather_images)

shadow_radius=w*1/5
dx=.2
dy=.2
feather_images=crop_images(feather_images,fh+shadow_radius,fw+shadow_radius,origin='center')
feather_images=with_drop_shadows(feather_images,x=shadow_radius*dx,y=shadow_radius*dy,color='black',blur=shadow_radius,opacity=.5)

feather_images=as_byte_images(feather_images)
feather_images=feather_images[::-1]
peacock_image=overlay_images(feather_images)
peacock_image=crop_image_zeros(peacock_image)
display_alpha_image(peacock_image)
