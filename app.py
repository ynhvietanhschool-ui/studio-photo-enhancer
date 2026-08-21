import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import os
import io

st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer (HD Quality)")

# Lấy API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

    st.sidebar.header("⚙️ Cấu hình Studio")
    style_option = st.sidebar.selectbox("Phong cách:", ["Tự nhiên", "Điện ảnh", "Rực rỡ"])
    smooth_val = st.sidebar.slider("Độ mịn da nhẹ", 1, 5, 2)
    brightness_val = st.sidebar.slider("Độ sáng", 0.8, 1.3, 1.05)
    contrast_val = st.sidebar.slider("Độ tương phản", 0.8, 1.3, 1.1)
    upscale_ratio = st.sidebar.select_slider("Tăng độ nét & Kích thước (Chống bể):", options=[2, 3, 4], value=3)

    uploaded_file = st.file_uploader("Tải ảnh cần nâng cấp lên:", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        orig_image = Image.open(uploaded_file).convert("RGB")
        
        with col1:
            st.subheader("🖼️ Ảnh gốc")
            st.image(orig_image, use_container_width=True)
            st.caption(f"Kích thước gốc: {orig_image.width} x {orig_image.height} px")

        if st.button("🚀 Nâng cấp Studio HD"):
            with st.spinner("Đang tăng độ phân giải và tối ưu chi tiết..."):
                try:
                    # 1. Phóng to kích thước chống bể nét (Super Resolution Lanczos)
                    new_size = (orig_image.width * upscale_ratio, orig_image.height * upscale_ratio)
                    processed_img = orig_image.resize(new_size, Image.Resampling.LANCZOS)

                    # 2. Làm mịn da nhẹ dịu
                    for _ in range(smooth_val):
                        processed_img = processed_img.filter(ImageFilter.SMOOTH)

                    # 3. Tăng độ sắc nét vừa phải
                    enhancer_sharp = ImageEnhance.Sharpness(processed_img)
                    processed_img = enhancer_sharp.enhance(1.3)

                    # 4. Điều chỉnh độ sáng và tương phản
                    enhancer_bright = ImageEnhance.Brightness(processed_img)
                    processed_img = enhancer_bright.enhance(brightness_val)

                    enhancer_contrast = ImageEnhance.Contrast(processed_img)
                    processed_img = enhancer_contrast.enhance(contrast_val)

                    # 5. Phân tích báo cáo bằng AI
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    prompt = f"Phân tích ảnh chân dung này và viết báo cáo nâng cấp studio ngắn gọn (Phong cách {style_option}) bằng tiếng Việt."
                    response = model.generate_content([prompt, orig_image])

                    # Xuất file JPEG chất lượng 100%
                    buf = io.BytesIO()
                    processed_img.save(buf, format="JPEG", quality=100, subsampling=0)
                    byte_im = buf.getvalue()

                    with col2:
                        st.subheader("✨ Ảnh Studio HD Tối Ưu")
                        st.image(processed_img, use_container_width=True)
                        st.caption(f"Kích thước xuất: {processed_img.width} x {processed_img.height} px")
                        
                        st.download_button(
                            label="📥 Tải ảnh Studio HD sắc nét",
                            data=byte_im,
                            file_name="studio_enhanced_hd.jpg",
                            mime="image/jpeg"
                        )
                        
                        st.markdown("---")
                        st.write("📋 **Báo cáo tối ưu từ AI:**")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
