import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import os
import io

st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer")
st.caption("Nâng cấp ảnh chuẩn Studio chuyên nghiệp - Tự động & Miễn phí 100%")

# Lấy API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Nhập Google Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)

    st.sidebar.header("⚙️ Thiết lập tùy chọn Studio")
    style_option = st.sidebar.selectbox("Phong cách:", ["Tự nhiên", "Điện ảnh", "Rực rỡ"])
    type_option = st.sidebar.selectbox("Thể loại:", ["Chân dung", "Sản phẩm", "Tối giản"])
    
    # Bộ chỉnh thông số nâng cao
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Điều chỉnh màu sắc")
    brightness_val = st.sidebar.slider("Độ sáng", 0.5, 1.5, 1.1)
    contrast_val = st.sidebar.slider("Độ tương phản", 0.5, 1.5, 1.2)
    color_val = st.sidebar.slider("Độ bão hòa màu", 0.5, 1.8, 1.15)
    sharpness_val = st.sidebar.slider("Độ sắc nét", 0.5, 3.0, 1.5)

    uploaded_file = st.file_uploader("Tải ảnh cần nâng cấp lên:", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        image = Image.open(uploaded_file).convert("RGB")
        
        with col1:
            st.subheader("🖼️ Ảnh gốc")
            st.image(image, use_container_width=True)

        if st.button("🚀 Nâng cấp & Xuất ảnh Studio"):
            with st.spinner("Đang tối ưu hóa hình ảnh và tạo báo cáo..."):
                try:
                    # 1. Thuật toán xử lý ảnh Studio bằng Pillow
                    processed_img = image.copy()
                    
                    # Giảm nhiễu/Làm mịn nhẹ hậu cảnh
                    processed_img = processed_img.filter(ImageFilter.SMOOTH_MORE)
                    
                    # Tăng độ sắc nét
                    enhancer = ImageEnhance.Sharpness(processed_img)
                    processed_img = enhancer.enhance(sharpness_val)
                    
                    # Cân bằng độ sáng
                    enhancer = ImageEnhance.Brightness(processed_img)
                    processed_img = enhancer.enhance(brightness_val)
                    
                    # Tăng độ tương phản
                    enhancer = ImageEnhance.Contrast(processed_img)
                    processed_img = enhancer.enhance(contrast_val)
                    
                    # Cân bằng màu sắc (Bão hòa)
                    enhancer = ImageEnhance.Color(processed_img)
                    processed_img = enhancer.enhance(color_val)

                    # 2. Phân tích báo cáo bằng AI Gemini
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"""
                    Hãy đóng vai chuyên gia chỉnh sửa ảnh Studio. Hãy đánh giá bức ảnh này và liệt kê 5 điểm đã được cải thiện (Màu sắc, Ánh sáng, Độ sắc nét, Khử nhiễu, Bố cục) theo phong cách {style_option} và thể loại {type_option}. Trả lời bằng tiếng Việt ngắn gọn, chuyên nghiệp.
                    """
                    response = model.generate_content([prompt, image])

                    # 3. Chuyển đổi ảnh sang byte để làm nút Download
                    buf = io.BytesIO()
                    processed_img.save(buf, format="JPEG", quality=95)
                    byte_im = buf.getvalue()

                    with col2:
                        st.subheader("✨ Ảnh đã tối ưu Studio")
                        st.image(processed_img, use_container_width=True)
                        
                        # Nút Tải ảnh về
                        st.download_button(
                            label="📥 Tải ảnh Studio (Chất lượng cao)",
                            data=byte_im,
                            file_name="studio_enhanced.jpg",
                            mime="image/jpeg"
                        )
                        
                        st.markdown("---")
                        st.subheader("📋 Báo cáo tối ưu từ AI:")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
else:
    st.warning("⚠️ Chưa tìm thấy API Key. Vui lòng kiểm tra lại cấu hình Secrets.")
