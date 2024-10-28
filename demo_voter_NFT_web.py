import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Cập nhật URL của API
API_URL = "https://mantea-mongodbnft.hf.space"

# Cập nhật hàm register_voter để thêm role
def register_voter(name, group, role):  # Thêm tham số role
    response = requests.post(f"{API_URL}/register-voter", 
                           json={"name": name, "group": group, "role": role})  # Thêm role vào JSON
    if response.status_code == 200:
        return response.json()['id']
    else:
        st.error("Không thể đăng ký người bình chọn")
        return None

def vote_for_file(voter_id, file_id):
    response = requests.post(f"{API_URL}/vote-by-voter", json={"voter_id": voter_id, "file_id": file_id})
    if response.status_code == 200:
        st.success("Bình chọn thành công!")
    else:
        st.error(f"Không thể bình chọn: {response.json().get('message')}")

def get_voter_info(voter_id):
    response = requests.get(f"{API_URL}/get-voter?id={voter_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Không thể lấy thông tin người bình chọn")
        return None

def get_files():
    response = requests.get(f"{API_URL}/get-files")
    if response.status_code == 200:
        return response.json()['data']
    else:
        st.error("Không thể lấy danh sách file từ server")
        return []

st.title("Demo Bình chọn NFT")

# Đăng ký người bình chọn
with st.sidebar:
    st.header("Đăng ký người bình chọn")
    name = st.text_input("Tên")
    group = st.text_input("Nhóm")
    role = st.selectbox("Vai trò", ["contestant", "judge"])  # Thêm selectbox cho role
    if st.button("Đăng ký"):
        voter_id = register_voter(name, group, role)  # Thêm role vào hàm
        if voter_id:
            st.session_state['voter_id'] = voter_id
            st.success("Đăng ký thành công!")

# Hiển thị thông tin người bình chọn
if 'voter_id' in st.session_state:
    voter_info = get_voter_info(st.session_state['voter_id'])
    if voter_info:
        st.sidebar.write(f"Tên: {voter_info['name']}")
        st.sidebar.write(f"Nhóm: {voter_info['group']}")
        st.sidebar.write(f"Vai trò: {voter_info['role']}")  # Thêm hiển thị role
        max_votes = 5 if voter_info['role'] == 'judge' else 2
        st.sidebar.write(f"Số lượt bình chọn: {voter_info['number_of_votes']}/{max_votes}")

# Hiển thị danh sách file và nút bình chọn
files = get_files()
for file in files:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        try:
            response = requests.get(file['url'])
            img = Image.open(BytesIO(response.content))
            st.image(img, caption=file['title'], use_column_width=True)
        except:
            st.error(f"Không thể hiển thị ảnh: {file['title']}")
    
    with col2:
        st.write(f"Số lượt bình chọn: {file.get('votes', 0)}")
        if 'voter_id' in st.session_state and st.button(f"Bình chọn", key=file['id']):
            vote_for_file(st.session_state['voter_id'], file['id'])

# Nút để làm mới trang
if st.button("Làm mới trang"):
    st.rerun()
