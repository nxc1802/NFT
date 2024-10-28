import streamlit as st
import requests

# Cập nhật URL của API
API_URL = "https://mantea-mongodbnft.hf.space"
FIREBASE_URL = "https://mantea-firebasenft.hf.space/upload/"  # Đã thêm dấu / ở cuối

# Tiêu đề của ứng dụng
st.title("Image Upload Demo")

# Tạo một uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Kiểm tra nếu có file được upload
if uploaded_file is not None:
    # Hiển thị ảnh đã upload
    st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)

    # Tạo các trường nhập liệu cho title và group
    title = st.text_input("Enter title")
    group = st.text_input("Enter group")

    # Tạo nút để upload ảnh lên Firebase và MongoDB
    if st.button("Upload to Firebase & MongoDB"):
        # Tạo yêu cầu POST tới Firebase
        try:
            firebase_response = requests.post(
                FIREBASE_URL,
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            )

            # Kiểm tra phản hồi từ Firebase
            if firebase_response.status_code == 200:
                st.success("File uploaded to Firebase successfully!")
                firebase_url = firebase_response.json().get("url")
                st.write("Firebase File URL:", firebase_url)

                # Tạo form data để gửi lên MongoDB
                form_data = {
                    'title': title,
                    'group': group,
                    'url': firebase_url
                }

                # Tạo yêu cầu POST tới server MongoDB
                mongo_response = requests.post(
                    f"{API_URL}/upload-files", 
                    data=form_data  # Sử dụng data thay vì json
                )

                # Kiểm tra phản hồi từ server MongoDB
                if mongo_response.status_code == 200:
                    try:
                        mongo_result = mongo_response.json()
                        st.success("File information uploaded to MongoDB successfully!")
                        st.write("MongoDB File ID:", mongo_result.get("id"))
                    except requests.exceptions.JSONDecodeError:
                        st.error(f"MongoDB upload failed: Invalid JSON response")
                        st.write("Response content:", mongo_response.text)
                else:
                    st.error(f"MongoDB upload failed with status code: {mongo_response.status_code}")
                    st.write("Response content:", mongo_response.text)
            else:
                st.error(f"Firebase upload failed with status code: {firebase_response.status_code}")
                st.write("Response content:", firebase_response.text)
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred during the upload process: {str(e)}")

# Thêm một nút để kiểm tra kết nối với Firebase
if st.button("Check Firebase Connection"):
    try:
        response = requests.get(FIREBASE_URL)
        st.write(f"Status code: {response.status_code}")
        st.write(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Firebase: {str(e)}")
