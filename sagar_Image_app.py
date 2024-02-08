import streamlit as st
from PIL import Image
import io
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
import requests
import json
import os
import base64

def download_json_file(url, output_path):
    response = requests.get(url)
    with open(output_path, 'w') as json_file:
        json_file.write(response.text)

json_file_path = "imapp.json"
if not os.path.exists(json_file_path):
    url = "https://github.com/Sagarnr1997/Image_app/blob/main/imapp.json?raw=true"
    download_json_file(url, json_file_path)

def authenticate_drive(json_file_path):
    creds = service_account.Credentials.from_service_account_file(json_file_path, scopes=['https://www.googleapis.com/auth/drive'])
    return creds

def upload_to_drive(image, json_file_path):
    drive_service = build('drive', 'v3', credentials=authenticate_drive(json_file_path))

    file_metadata = {
        'name': 'uploaded_image.jpg', # Change the file name if needed
        'mimeType': 'image/jpeg'
    }
    media = MediaIoBaseUpload(image, mimetype='image/jpeg')

    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

js_code = """
<script>
// Your JavaScript code goes here
// This function will compress the image using canvas and return the base64 encoded string
function compressImage(base64Str, maxWidth, maxHeight, quality) {
    var img = new Image();
    img.src = base64Str;

    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');

    var width = img.width;
    var height = img.height;

    if (width > height) {
        if (width > maxWidth) {
            height *= maxWidth / width;
            width = maxWidth;
        }
    } else {
        if (height > maxHeight) {
            width *= maxHeight / height;
            height = maxHeight;
        }
    }

    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(img, 0, 0, width, height);

    return canvas.toDataURL('image/jpeg', quality);
}

// This function is called when the page is loaded
window.onload = function() {
    var images = document.querySelectorAll('.compressed-img');

    images.forEach(function(image) {
        var base64Str = image.src;
        var compressedBase64 = compressImage(base64Str, 100, 100, 0.5);
        image.src = compressedBase64;
    });
};
</script>
"""

def main():
    st.title("Mobile Gallery and Selection")

    st.write(js_code, unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        uploaded_images = [Image.open(img) for img in uploaded_files]

        st.write("<style> .gallery { display: flex; flex-wrap: wrap; } .gallery img { width: 100px; height: 100px; object-fit: cover; margin: 5px; cursor: pointer; } </style>", unsafe_allow_html=True)
        st.write("<div class='gallery'>")
        for idx, img in enumerate(uploaded_images):
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=100)
            img_io.seek(0)

            file_id = upload_to_drive(img_io, json_file_path)
            st.image(img, caption=f"Image {idx + 1} uploaded to Google Drive. File ID: {file_id}", use_column_width=True)
            st.write("")

        st.write("</div>")

        if st.button("Download Selected Images"):
            selected_images = []
            for idx, img in enumerate(uploaded_images):
                checkbox_val = st.checkbox(f"Select Image {idx + 1}", key=f"checkbox_{idx}")
                if checkbox_val:
                    selected_images.append(img)

            for idx, img in enumerate(selected_images):
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG', quality=100)
                img_io.seek(0)

                st.markdown(f"#### Download Image {idx + 1} ####")
                st.download_button(
                    label=f"Download Image {idx + 1}",
                    data=img_io,
                    file_name=f"compressed_image_{idx + 1}.jpg",
                    mime="image/jpeg",
                    key=f"download_button_{idx}"
                )
                st.write("")

if st.button("Clear All"):
    st.write("Clearing all images and selections...")
    st.empty()

if __name__ == "__main__":
    main()
