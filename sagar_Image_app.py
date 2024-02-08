import streamlit as st
from PIL import Image
import io
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
import requests

# Initialize Firebase app
response = requests.get("https://github.com/Sagarnr1997/Image_app/blob/main/imapp.json")
json_data = json.loads(response.text)

# Function to authenticate with Google Drive
def authenticate_drive():
    creds = service_account.Credentials.from_service_account_file(json_data, scopes=['https://www.googleapis.com/auth/drive'])
    return creds

# Function to upload image to Google Drive
def upload_to_drive(image):
    drive_service = build('drive', 'v3', credentials=authenticate_drive())

    file_metadata = {
        'name': 'uploaded_image.jpg', # Change the file name if needed
        'mimeType': 'image/jpeg'
    }
    media = MediaIoBaseUpload(image, mimetype='image/jpeg')

    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# JavaScript function for client-side image resizing and compression
js_code = """
<script>
// Your JavaScript code goes here
</script>
"""

# Function to compress image
def compress_image(image, quality=50):
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG', quality=quality)
    img_io.seek(0)
    return img_io

def main():
    st.title("Mobile Gallery and Selection")

    # Display the JavaScript code in the Streamlit app
    st.write(js_code, unsafe_allow_html=True)

    # Upload images and call the JavaScript function when files are selected
    st.write("Upload Images")
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        uploaded_images = [Image.open(img) for img in uploaded_files]

        # Display images in a mobile gallery format
        st.write("<style> .gallery { display: flex; flex-wrap: wrap; } .gallery img { width: 100px; height: 100px; object-fit: cover; margin: 5px; cursor: pointer; } </style>", unsafe_allow_html=True)
        st.write("<div class='gallery'>")
        for idx, img in enumerate(uploaded_images):
            # Compress the image
            compressed_img = compress_image(img)

            # Display the image with a checkbox for selection
            st.write(f"<label for='img_{idx}'><img id='img_{idx}' src='data:image/png;base64,{compressed_img}' /></label><br>", unsafe_allow_html=True)

            # Upload the image to Google Drive
            file_id = upload_to_drive(compressed_img)
            st.write(f"Image {idx + 1} uploaded to Google Drive. File ID: {file_id}")

        st.write("</div>")
        
        # Download button for selected images
        if st.button("Download Selected Images"):
            selected_images = []
            for idx, img in enumerate(uploaded_images):
                checkbox_val = st.checkbox(f"Select Image {idx + 1}", key=f"checkbox_{idx}")
                if checkbox_val:
                    selected_images.append(img)

            for idx, img in enumerate(selected_images):
                # Compress the image
                compressed_img = compress_image(img)

                # Download the compressed image
                st.download_button(
                    label=f"Download Image {idx + 1}",
                    data=compressed_img,
                    file_name=f"compressed_image_{idx + 1}.jpg",
                    mime="image/jpeg"
                )

if __name__ == "__main__":
    main()
