import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Cập nhật URL của API
API_URL = "https://mantea-mongodbnft.hf.space"

# Hàm để lấy danh sách các file từ server
def get_files():
    response = requests.get(f"{API_URL}/get-files")
    if response.status_code == 200:
        return response.json()['data']
    else:
        st.error("Không thể lấy danh sách file từ server")
        return []

# Hàm để bình chọn cho một file
def vote_for_file(file_id):
    response = requests.post(f"{API_URL}/vote", json={"id": file_id})
    if response.status_code == 200:
        st.success("Bình chọn thành công!")
    else:
        st.error("Không thể bình chọn. Vui lòng thử lại.")

# Hàm để lấy số lượng bình chọn cho một file
def get_votes(file_id):
    response = requests.get(f"{API_URL}/get-votes?id={file_id}")
    if response.status_code == 200:
        return response.json()['votes']
    else:
        st.error("Không thể lấy số lượng bình chọn")
        return 0

# Tiêu đề của ứng dụng
st.title("Nội dung bình chọn NFT")

# Lấy danh sách các file
files = get_files()

# Hiển thị các file và nút bình chọn
for file in files:
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        try:
            response = requests.get(file['url'])
            img = Image.open(BytesIO(response.content))
            st.image(img, caption=file['title'], use_column_width=True)
        except:
            st.error(f"Không thể hiển thị ảnh: {file['title']}")
    
    with col2:
        if st.button(f"Bình chọn", key=file['id']):
            vote_for_file(file['id'])
    
    with col3:
        votes = get_votes(file['id'])
        st.write(f"Số lượt bình chọn: {votes}")
    
    st.write("---")

# Nút để làm mới trang
if st.button("Làm mới trang"):
    st.rerun()
