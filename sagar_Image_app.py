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

# Function to download the JSON file from a URL
def download_json_file(url, output_path):
    response = requests.get(url)
    with open(output_path, 'w') as json_file:
        json_file.write(response.text)

# Download the JSON file if it does not exist
json_file_path = "imapp.json"
if not os.path.exists(json_file_path):
    url = "https://github.com/Sagarnr1997/Image_app/blob/main/imapp.json?raw=true"
    download_json_file(url, json_file_path)

# Authenticate Google Drive
def authenticate_drive(json_file_path):
    creds = service_account.Credentials.from_service_account_file(json_file_path, scopes=['https://www.googleapis.com/auth/drive'])
    return creds

# Upload image to Google Drive
def upload_to_drive(image, json_file_path):
    drive_service = build('drive', 'v3', credentials=authenticate_drive(json_file_path))
    file_metadata = {
        'name': 'uploaded_image.jpg', # Change the file name if needed
        'mimeType': 'image/jpeg'
    }
    media = MediaIoBaseUpload(image, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Streamlit app
def main():
    st.title("Mobile Gallery and Selection")

    js_code = """
    <script>
    // Function to prompt download on clicking download icon
    function downloadImage(imageData, fileName) {
        const link = document.createElement('a');
        link.href = imageData;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

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

    st.write(js_code, unsafe_allow_html=True)

    # CSS for mobile gallery
    st.write("<style>.gallery { display: flex; flex-wrap: wrap; justify-content: center; } .gallery img { position: relative; width: 80px; height: 80px; object-fit: cover; margin: 5px; cursor: pointer; border-radius: 5px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease; } .gallery img:hover { transform: scale(1.1); } .download-icon { position: absolute; top: 5px; right: 5px; width: 20px; height: 20px; cursor: pointer; }</style>", unsafe_allow_html=True)

    # File uploader
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        uploaded_images = [Image.open(img) for img in uploaded_files]

        # Display images in gallery format
        st.write("<div class='gallery'>")
        for idx, img in enumerate(uploaded_images):
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=100)
            img_io.seek(0)

            file_id = upload_to_drive(img_io, json_file_path)

            # Display image with download icon
            st.write(f"<div class='image-container'><img class='compressed-img' src='data:image/jpeg;base64,{base64.b64encode(img_io.getvalue()).decode()}' /><img class='download-icon' src='https://cdn-icons-png.flaticon.com/512/747/747376.png' onclick='downloadImage(\"{img_io}\", \"image_{idx + 1}.jpg\")' /></div>", unsafe_allow_html=True)

            st.write(f"Image {idx + 1} uploaded to Google Drive. File ID: {file_id}")

        st.write("</div>")

if __name__ == "__main__":
    main()
