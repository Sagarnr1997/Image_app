import streamlit as st
from PIL import Image
import io
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
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

# Path to store the downloaded JSON file
json_file_path = "imapp.json"

# Download the JSON file if it does not exist
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

# Function to list files in Google Drive
def list_drive_files(json_file_path):
    drive_service = build('drive', 'v3', credentials=authenticate_drive(json_file_path))
    results = drive_service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    return items

# Function to download an image from Google Drive
def download_from_drive(file_id, json_file_path):
    drive_service = build('drive', 'v3', credentials=authenticate_drive(json_file_path))
    request = drive_service.files().get_media(fileId=file_id)
    downloaded_img = io.BytesIO()
    downloader = MediaIoBaseDownload(downloaded_img, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    downloaded_img.seek(0)
    return downloaded_img

# JavaScript code for image compression and download
js_code = """
<script>
// Function to prompt download on clicking the image
function downloadImage(imageData, fileName) {
    const link = document.createElement('a');
    link.href = imageData;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// This function is called when the page is loaded
window.onload = function() {
    var downloadIcons = document.querySelectorAll('.download-icon');
    downloadIcons.forEach(function(icon) {
        icon.addEventListener('click', function(event) {
            var imageAlt = event.target.getAttribute('data-image-alt');
            var imageData = event.target.getAttribute('data-image-data');
            downloadImage(imageData, imageAlt);
        });
    });
};
</script>
"""

# Main function
def main():
    st.title("Mobile Gallery and Selection")

    # Write JavaScript code
    st.write(js_code, unsafe_allow_html=True)

    # File uploader for local images
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    # Display uploaded images and upload to Google Drive
    if uploaded_files:
        st.write("Uploaded Images:")
        for idx, img_file in enumerate(uploaded_files):
            img = Image.open(img_file)
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=100)
            img_io.seek(0)
            file_id = upload_to_drive(img_io, json_file_path)

    # Display images from Google Drive
    drive_files = list_drive_files(json_file_path)
    if drive_files:
        st.write("Images in Google Drive:")
        for file in drive_files:
            if 'image' in file['mimeType']:
                img_data = download_from_drive(file['id'], json_file_path)
                img = Image.open(img_data)
                
                # Display image with download icon
                st.image(img, caption=file['name'], use_column_width=True)
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <a href='data:application/octet-stream;base64,{base64.b64encode(img_data.getvalue()).decode()}' download='{file['name']}'>
                            <img src='https://www.freeiconspng.com/uploads/download-icon-png-5.png' style='width: 24px; height: 24px;' class='download-icon' data-image-alt='{file['name']}' data-image-data='{base64.b64encode(img_data.getvalue()).decode()}'>
                        </a>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
