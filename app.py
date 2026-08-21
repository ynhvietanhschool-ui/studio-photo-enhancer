import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import os
import io

st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer (HD Quality)")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

    st.sidebar.header("⚙️ Thiết lập tùy chọn Studio")
    style_option = st.sidebar.selectbox("Phong cách:", ["Tự nhiên", "Điện ảnh", "Rực rỡ"])
    type_option = st.sidebar.selectbox("Thể loại:", ["Chân dung", "Sản phẩm", "Tối giản"])
    
    # Thêm tùy chọn phóng to chất lượng cao
    upscale_factor = st.sidebar.select_slider("Tăng độ phân giải (Upscale):", options=[1, 2, 4], value=2)

    uploaded_file = st.file_uploader("Tải ảnh cần nâng cấp lên:", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        # Đọc ảnh gốc giữ nguyên chuẩn kích thước
        orig_image = Image.open(uploaded_file).convert("RGB")
        
        with col1:
            st.subheader("🖼️ Ảnh gốc")
            st.image(orig_image, use_container_width=True)
            st.caption(f"Kích thước gốc: {orig_image.width} x {orig_image.height} px")

        if st.button("🚀 Nâng cấp HD & Xuất ảnh Studio"):
            with st.spinner("Đang tối ưu hóa độ phân giải và màu sắc..."):
                try:
                    processed_img = orig_image.copy()

                    # 1. Phóng to kích thước ảnh (Upscale) không làm mờ nét
                    if upscale_factor > 1:
                        new_size = (processed_img.width * upscale_factor, processed_img.height * upscale_factor)
                        processed_img = processed_img.resize(new_size, Image.Resampling.LANCZOS)

                    # 2. Thuật toán làm nét và tối ưu chi tiết (Sharpen Filter)
                    processed_img = processed_img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

                    # 3. Cân bằng màu sắc & Tương phản Studio
                    enhancer_contrast = ImageEnhance.Contrast(processed_img)
                    processed_img = enhancer_contrast.enhance(1.25)

                    enhancer_color = ImageEnhance.Color(processed_img)
                    processed_img = enhancer_color.enhance(1.15)

                    enhancer_bright = ImageEnhance.Brightness(processed_img)
                    processed_img = enhancer_bright.enhance(1.05)

                    # 4. Phân tích báo cáo AI
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    prompt = f"Phân tích ảnh chân dung này và viết báo cáo nâng cấp studio ngắn gọn (Phong cách {style_option}) bằng tiếng Việt."
                    response = model.generate_content([prompt, orig_image])

                    # 5. Xuất file JPEG chất lượng tối đa (Quality 100, không nén)
                    buf = io.BytesIO()
                    processed_img.save(buf, format="JPEG", quality=100, subsampling=0)
                    byte_im = buf.getvalue()

                    with col2:
                        st.subheader("✨ Ảnh Studio HD")
                        st.image(processed_img, use_container_width=True)
                        st.caption(f"Kích thước xuất: {processed_img.width} x {processed_img.height} px")
                        
                        st.download_button(
                            label="📥 Tải ảnh HD sắc nét về máy",
                            data=byte_im,
                            file_name="studio_enhanced_hd.jpg",
                            mime="image/jpeg"
                        )
                        
                        st.markdown("---")
                        st.write("📋 **Báo cáo tối ưu từ AI:**")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
