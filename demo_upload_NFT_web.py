import streamlit as st
import requests

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
        firebase_response = requests.post(
            "https://mantea-nft.hf.space/upload/",
            files={"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
        )

        # Kiểm tra phản hồi từ Firebase
        if firebase_response.status_code == 200:
            st.success("File uploaded to Firebase successfully!")
            firebase_url = firebase_response.json().get("url")
            st.write("Firebase File URL:", firebase_url)
        else:
            st.error(f"Firebase upload failed: {firebase_response.json().get('detail')}")

        # Sau khi upload lên Firebase, ta sẽ upload file thông tin lên server local
        # Do không có `file_path`, dùng `uploaded_file` từ streamlit như sau:
        upload_files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
        data = {
            'title': title,
            'group': group,
            'url': firebase_url,
            'vote': 0
        }

        # Tạo yêu cầu POST tới server MongoDB (local)
        mongo_response = requests.post("http://localhost:5000/upload-files", files=upload_files, data=data)

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
