import streamlit as st
import google.generativeai as genai
import replicate
from PIL import Image
import os
import requests
from io import BytesIO

st.set_page_config(page_title="Studio AI Photo Enhancer", layout="wide")
st.title("📸 AI Studio Photo Enhancer")

# Lấy API Keys từ Secrets
gemini_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
replicate_key = st.secrets.get("REPLICATE_API_TOKEN") if "REPLICATE_API_TOKEN" in st.secrets else os.getenv("REPLICATE_API_TOKEN")

if gemini_key:
    genai.configure(api_key=gemini_key)

st.sidebar.header("⚙️ Thiết lập tùy chọn")
style_option = st.sidebar.selectbox("Phong cách:", ["Tự nhiên", "Điện ảnh", "Rực rỡ"])
type_option = st.sidebar.selectbox("Thể loại:", ["Chân dung", "Sản phẩm", "Tối giản"])

uploaded_file = st.file_uploader("Tải ảnh cần nâng cấp lên:", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    image = Image.open(uploaded_file)
    
    with col1:
        st.subheader("🖼️ Ảnh gốc")
        st.image(image, use_container_width=True)

    if st.button("🚀 Nâng cấp & Sinh ảnh Studio"):
        if not replicate_key:
            st.error("⚠️ Cần cấu hình REPLICATE_API_TOKEN trong Secrets để sinh ảnh thật.")
        else:
            with st.spinner("Đang tạo ảnh chất lượng Studio..."):
                try:
                    # 1. Dùng Gemini để phân tích báo cáo
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    response = model.generate_content(["Viết báo cáo cải thiện ảnh studio ngắn gọn bằng tiếng Việt", image])
                    
                    # 2. Dùng Replicate để tạo ảnh mới thật
                    output = replicate.run(
                        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                        input={
                            "prompt": f"professional studio photo, 8k resolution, {style_option} lighting, {type_option} photography, highly detailed",
                            "image": uploaded_file
                        }
                    )
                    
                    # 3. Hiển thị ảnh kết quả & nút Tải về
                    img_url = output[0]
                    img_data = requests.get(img_url).content
                    result_img = Image.open(BytesIO(img_data))
                    
                    with col2:
                        st.subheader("✨ Ảnh đã tối ưu Studio")
                        st.image(result_img, use_container_width=True)
                        
                        # Nút Tải ảnh về
                        st.download_button(
                            label="📥 Tải ảnh Studio về máy",
                            data=img_data,
                            file_name="studio_enhanced.jpg",
                            mime="image/jpeg"
                        )
                        
                        st.markdown("---")
                        st.write("📋 **Báo cáo cải thiện:**")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Lỗi xử lý: {e}")
