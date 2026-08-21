import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import os
import io

st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer (Mịn da & HD Super Resolution)")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

    st.sidebar.header("⚙️ Thiết lập Studio")
    smooth_val = st.sidebar.slider("Độ mịn da", 1, 9, 3)
    brightness_val = st.sidebar.slider("Độ sáng", -20, 20, 5)
    contrast_val = st.sidebar.slider("Độ tương phản", 0.9, 1.3, 1.05)
    
    # Tùy chọn tăng kích thước chống bể ảnh
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
            with st.spinner("Đang tăng độ phân giải và xử lý mịn da..."):
                try:
                    # 1. Phóng to kích thước ảnh trước (Super Resolution) bằng thuật toán Lanczos4 chống bể
                    img_np = np.array(orig_image)
                    h, w = img_np.shape[:2]
                    new_w, new_h = w * upscale_ratio, h * upscale_ratio
                    
                    resized_np = cv2.resize(img_np, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                    img_bgr = cv2.cvtColor(resized_np, cv2.COLOR_RGB2BGR)

                    # 2. Xử lý mịn da trên độ phân giải cao
                    d = smooth_val * 2 + 1
                    smoothed = cv2.bilateralFilter(img_bgr, d, 50, 50)

                    # 3. Cân bằng ánh sáng dịu nhẹ
                    adjusted = cv2.convertScaleAbs(smoothed, alpha=contrast_val, beta=brightness_val)

                    # 4. Trộn với ảnh nét gốc (80% mịn + 20% nét thật)
                    final_bgr = cv2.addWeighted(adjusted, 0.8, img_bgr, 0.2, 0)

                    # Chuyển về PIL Image
                    final_rgb = cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB)
                    processed_img = Image.fromarray(final_rgb)

                    # 5. Tăng nhẹ độ sắc nét chi tiết (Unsharp)
                    enhancer = ImageEnhance.Sharpness(processed_img)
                    processed_img = enhancer.enhance(1.2)

                    # Xuất file chất lượng cao
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

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
