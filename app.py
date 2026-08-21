import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import os
import io

st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer")

# Tự động đọc API Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

    st.sidebar.header("⚙️ Thiết lập Studio")
    style_option = st.sidebar.selectbox("Phong cách:", ["Tự nhiên", "Điện ảnh", "Rực rỡ"])
    brightness_val = st.sidebar.slider("Độ sáng", 0.8, 1.3, 1.05)
    contrast_val = st.sidebar.slider("Độ tương phản", 0.8, 1.3, 1.1)
    upscale_ratio = st.sidebar.select_slider("Tỷ lệ phóng to (Làm nét):", options=[1, 2, 3], value=2)

    uploaded_file = st.file_uploader("Tải ảnh cần nâng cấp lên:", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        orig_image = Image.open(uploaded_file).convert("RGB")
        
        with col1:
            st.subheader("🖼️ Ảnh gốc")
            st.image(orig_image, use_container_width=True)

        if st.button("🚀 Nâng cấp Studio"):
            with st.spinner("Đang xử lý..."):
                try:
                    # 1. Tăng kích thước HD chống bể
                    if upscale_ratio > 1:
                        new_size = (orig_image.width * upscale_ratio, orig_image.height * upscale_ratio)
                        processed_img = orig_image.resize(new_size, Image.Resampling.LANCZOS)
                    else:
                        processed_img = orig_image.copy()

                    # 2. Chỉnh độ sáng & tương phản
                    enhancer_bright = ImageEnhance.Brightness(processed_img)
                    processed_img = enhancer_bright.enhance(brightness_val)

                    enhancer_contrast = ImageEnhance.Contrast(processed_img)
                    processed_img = enhancer_contrast.enhance(contrast_val)

                    # 3. Phân tích báo cáo AI Gemini
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    prompt = f"Viết báo cáo đánh giá ảnh chân dung phong cách {style_option} ngắn gọn 3 dòng bằng tiếng Việt."
                    response = model.generate_content([prompt, orig_image])

                    # 4. Xuất file JPEG HD
                    buf = io.BytesIO()
                    processed_img.save(buf, format="JPEG", quality=95)
                    byte_im = buf.getvalue()

                    with col2:
                        st.subheader("✨ Kết quả Studio")
                        st.image(processed_img, use_container_width=True)
                        
                        st.download_button(
                            label="📥 Tải ảnh Studio về máy",
                            data=byte_im,
                            file_name="studio_enhanced.jpg",
                            mime="image/jpeg"
                        )
                        
                        st.markdown("---")
                        st.write("📋 **Báo cáo từ AI:**")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
else:
    st.warning("⚠️ Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình Secrets.")
