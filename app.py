import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Cấu hình trang web
st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer")
st.caption("Nâng cấp ảnh chuẩn Studio chuyên nghiệp với 9 bước xử lý tự động")

# 2. Tự động lấy API Key từ hệ thống bảo mật (Secrets)
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")

# Nếu không tìm thấy key bảo mật, mới hiển thị ô nhập dự phòng
if not api_key:
    api_key = st.sidebar.text_input("Nhập Google Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)

    # 3. Tùy chọn nâng cao trên Sidebar
    st.sidebar.header("⚙️ Thiết lập tùy chọn")
    
    style_option = st.sidebar.selectbox(
        "Phong cách (Style):",
        ["Tự nhiên (Natural)", "Điện ảnh (Cinematic)", "Rực rỡ (Vibrant)"]
    )
    
    type_option = st.sidebar.selectbox(
        "Thể loại (Category):",
        ["Chân dung (Portrait)", "Sản phẩm (Product)", "Tối giản (Minimalist)"]
    )
    
    crop_aspect = st.sidebar.selectbox("Tỷ lệ khung hình (Crop):", ["Giữ nguyên", "1:1 (Square)", "4:5 (Instagram)", "16:9 (Landscape)"])

    # 4. Tải ảnh lên
    uploaded_file = st.file_uploader("Tải ảnh cần nâng cấp lên:", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        image = Image.open(uploaded_file)
        
        with col1:
            st.subheader("🖼️ Ảnh gốc")
            st.image(image, use_container_width=True)

        if st.button("🚀 Nâng cấp ảnh đạt chuẩn Studio"):
            with st.spinner("Đang xử lý ảnh qua 9 bước Studio..."):
                master_prompt = f"""
                You are an expert AI photo retoucher and image generator. Upgrade the provided image to professional studio quality.

                Strictly follow these requirements:
                1. Advanced Color Grading: Fix white balance, optimize contrast, and fine-tune color saturation naturally.
                2. Denoise & Sharpen: Remove digital noise and grain while sharpening key details (eyes, facial features, textures).
                3. Blemish & Defect Removal: Clean up skin blemishes, spots, and unwanted background distractions.
                4. Realistic Lighting Adjustment: Balance shadows and highlights to create studio lighting depth.
                5. Professional Composition & Crop: Re-frame and adjust perspective. Crop ratio preference: {crop_aspect}.
                6. Selected Style: {style_option}.
                7. Selected Category: {type_option}.
                8. Detailed Report: List every specific improvement made to the image in Vietnamese.
                9. Optimized Output: Generate and render the final high-resolution optimized studio-quality image.
                """

                try:
                    # Sử dụng mô hình xử lý đa phương thức
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([master_prompt, image])

                    with col2:
                        st.subheader("✨ Báo cáo & Kết quả Studio")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Có lỗi xảy ra trong quá trình xử lý: {e}")

else:
    st.warning("⚠️ Chưa tìm thấy API Key. Vui lòng cấu hình Secrets trên Streamlit Cloud hoặc nhập thủ công.")
