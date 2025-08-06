import streamlit as st
import numpy as np
import cv2
from rp import *
from image_stack import create_motion_blur_image

# Configure streamlit page
st.set_page_config(page_title="Motion Blur Image Generator", layout="wide")

st.title("🎬 Motion Blur Image Generator")
st.markdown("Generate motion blur effects from video files with interactive controls")

# Initialize session state
if 'video' not in st.session_state:
    st.session_state.video = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

# Sidebar for controls
with st.sidebar:
    st.header("📁 Video Settings")
    
    # Video path input
    video_path = st.text_input(
        "Video Path:", 
        value="https://www.shutterstock.com/shutterstock/videos/1100494195/preview/stock-footage-drone-footage-of-wetlands-offers-a-stunning-aerial-view-of-these-complex-environments-highlighting.webm",
        help="Enter the path to your video file"
    )
    
    if st.button("🔄 Load Video", type="secondary"):
        try:
            with st.spinner("Loading video..."):
                st.session_state.video = load_video(video_path, use_cache=True)
            st.success(f"✅ Loaded video: {len(st.session_state.video)} frames")
        except Exception as e:
            st.error(f"❌ Error loading video: {str(e)}")
    
    st.divider()
    
    # Motion parameters
    st.header("🎯 Motion Parameters")
    
    num_frames = st.slider("Frames", min_value=1, max_value=50, value=10, step=1)
    total_shift = st.slider("Total Shift", min_value=0, max_value=500, value=200, step=10)
    
    col1, col2 = st.columns(2)
    with col1:
        total_shift_x = st.slider("Shift X", min_value=0, max_value=500, value=200, step=10)
    with col2:
        total_shift_y = st.slider("Shift Y", min_value=0, max_value=500, value=100, step=10)
    
    frame_size = st.slider("Frame Size", min_value=64, max_value=512, value=256, step=16)
    alphas_exponent = st.slider("Alpha Exponent", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
    
    st.divider()
    
    # Shadow parameters
    st.header("🌑 Shadow Settings")
    
    shadow_shift = st.slider("Shadow Shift", min_value=0, max_value=50, value=10, step=1)
    shadow_blur = st.slider("Shadow Blur", min_value=0, max_value=100, value=30, step=5)
    shadow_opacity = st.slider("Shadow Opacity", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    
    st.divider()
    
    # Color settings
    st.header("🎨 Colors")
    
    shadow_color = st.color_picker("Shadow Color", value="#000000")
    background_color = st.color_picker("Background Color", value="#0000FF")
    
    st.divider()

# Main content area
if st.session_state.video is None:
    st.info("👆 Please load a video file using the sidebar controls to get started.")
    st.markdown("### How to use:")
    st.markdown("""
    1. **Load Video**: Enter the path to your video file and click 'Load Video'
    2. **Adjust Parameters**: Use the sliders to control motion blur effects
    3. **Customize Colors**: Pick colors for shadow and background
    4. **Generate**: Click 'Update Image' to create the motion blur effect
    """)
else:
    # Show video info and update button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"📊 Loaded video with {len(st.session_state.video)} frames")
    with col2:
        update_clicked = st.button("🚀 Update Image", type="primary", use_container_width=True)
    
    # Update image when button is clicked
    if update_clicked:
        try:
            with st.spinner("🎨 Generating motion blur image..."):
                # Generate motion blur image
                image = create_motion_blur_image(
                    st.session_state.video,
                    num_frames=num_frames,
                    total_shift=total_shift,
                    total_shift_x=total_shift_x,
                    total_shift_y=total_shift_y,
                    frame_size=frame_size,
                    shadow_shift=shadow_shift,
                    shadow_blur=shadow_blur,
                    shadow_color=shadow_color,
                    shadow_opacity=shadow_opacity,
                    alphas_exponent=alphas_exponent,
                )
                
                # Apply background and convert for display
                image = blend_images(background_color, image)
                image = as_rgb_image(image, copy=False)
                image = as_byte_image(image, copy=False)
                
                st.session_state.current_image = image
                
            st.success("✅ Image generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Display the current image
    if st.session_state.current_image is not None:
        st.subheader("🖼️ Motion Blur Result")
        
        # Display image at full width with better aspect ratio
        st.image(st.session_state.current_image, use_container_width=True)
        
        # Image info and controls below
        col1, col2, col3 = st.columns(3)
        with col1:
            height, width = st.session_state.current_image.shape[:2]
            st.metric("Dimensions", f"{width} × {height}")
        with col2:
            st.metric("Frames Used", num_frames)
        with col3:
            st.metric("Total Shift", total_shift)
            
        # Download button
        if st.button("💾 Save Image", use_container_width=True):
            # Convert to BGR for OpenCV
            bgr_image = cv2.cvtColor(st.session_state.current_image, cv2.COLOR_RGB2BGR)
            output_path = "motion_blur_output.png"
            cv2.imwrite(output_path, bgr_image)
            st.success(f"✅ Image saved as {output_path}")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit • Adjust parameters and click 'Update Image' to see changes")
