import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import cv2
import os
import io

st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer (Mịn da & Tự nhiên)")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

    st.sidebar.header("⚙️ Chỉnh sửa Studio Tự Nhiên")
    smooth_val = st.sidebar.slider("Độ mịn da (Lọc nhiễu)", 1, 9, 5)
    brightness_val = st.sidebar.slider("Độ sáng", -30, 30, 5)
    contrast_val = st.sidebar.slider("Độ tương phản", 0.8, 1.4, 1.05)

    uploaded_file = st.file_uploader("Tải ảnh cần nâng cấp lên:", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        orig_image = Image.open(uploaded_file).convert("RGB")
        
        with col1:
            st.subheader("🖼️ Ảnh gốc")
            st.image(orig_image, use_container_width=True)

        if st.button("🚀 Nâng cấp Studio Dịu Nhẹ"):
            with st.spinner("Đang làm mịn da và cân bằng ánh sáng..."):
                try:
                    # Chuyển ảnh sang dạng mảng OpenCV
                    img_np = np.array(orig_image)
                    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                    # 1. Thuật toán Bilateral Filter: Làm mịn da nhưng giữ lại đường nét mắt/mũi/miệng
                    d = smooth_val * 2 + 1
                    smoothed = cv2.bilateralFilter(img_bgr, d, 75, 75)

                    # 2. Điều chỉnh độ sáng & tương phản mềm mại
                    adjusted = cv2.convertScaleAbs(smoothed, alpha=contrast_val, beta=brightness_val)

                    # 3. Trộn nhẹ ảnh gốc và ảnh làm mịn để giữ độ chân thật (Blend 70% mịn + 30% gốc)
                    final_bgr = cv2.addWeighted(adjusted, 0.7, img_bgr, 0.3, 0)

                    # Chuyển lại về dạng PIL Image
                    final_rgb = cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB)
                    processed_img = Image.fromarray(final_rgb)

                    # Xuất file JPEG chất lượng
                    buf = io.BytesIO()
                    processed_img.save(buf, format="JPEG", quality=98)
                    byte_im = buf.getvalue()

                    with col2:
                        st.subheader("✨ Ảnh Studio đã tối ưu")
                        st.image(processed_img, use_container_width=True)
                        
                        st.download_button(
                            label="📥 Tải ảnh Studio về máy",
                            data=byte_im,
                            file_name="studio_enhanced_clean.jpg",
                            mime="image/jpeg"
                        )

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
