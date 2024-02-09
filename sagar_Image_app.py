import streamlit as st
import base64
import io
from PIL import Image, ImageOps
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.discovery import build
import requests
import json
import os

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
    // This function is called when the page is loaded
    window.onload = function() {
        var images = document.querySelectorAll('.compressed-img');

        images.forEach(function(image) {
            var base64Str = image.src;
            var compressedBase64 = compressImage(base64Str, 100, 100, 0.5);
            image.src = compressedBase64;
        });
    };

    // Function to open the image in a new tab
    function openImageInTab(imageElement) {
        var imageUrl = imageElement.src;
        window.open(imageUrl, 'Image');
    }

    // Function to rotate the image
    function rotateImage(imageElement, degree) {
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        var img = new Image();
        img.src = imageElement.src;
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(degree * Math.PI / 180);
        ctx.drawImage(img, -img.width / 2, -img.height / 2);
        ctx.restore();
        imageElement.src = canvas.toDataURL('image/jpeg');
    }
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
            st.image(img, caption=f"Image {idx + 1}", use_column_width=True)

            # Upload image to Google Drive
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=100)
            img_io.seek(0)
            file_id = upload_to_drive(img_io, json_file_path)

            # Add download icon for each image
            img_data = img_io.getvalue()
            st.markdown("<div style='text-align: center;'><a href='javascript:openImageInTab(document.querySelector(\".compressed-img:nth-child(" + str(idx + 1) + ")\"))'><img src='https://image.flaticon.com/icons/png/512/88/88950.png' style='width: 24px; height: 24px;'></a></div>", unsafe_allow_html=True)

            # Add compressed image for each uploaded image
            img_io.seek(0)
            img = Image.open(img_io)
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=50)
            img_io.seek(0)
            st.markdown("<img src='data:image/jpeg;base64," + base64.b64encode(img_io.read()).decode() + "' class='compressed-img' style='margin: 5px;'/>", unsafe_allow_html=True)

    // Add rotation functionality
    st.markdown("<div style='text-align: center;'><img src='https://image.flaticon.com/icons/png/512/1151/1151250.png' style='width: 24px; height: 24px;' title='Rotate counter-clockwise' onclick='rotateImage(document.querySelector(\".compressed-img:nth-child(" + str(idx + 1) + ")\"), -90)'></div>", unsafe_allow_html=True)

    # Add download functionality
    st.markdown("<div style='text-align: center;'><a href='javascript:downloadImage(document.querySelector(\".compressed-img:nth-child(" + str(idx + 1) + ")\").src, \"image" + str(idx + 1) + ".jpg\")'><img src='https://image.flaticon.com/icons/png/512/94/94944.png' style='width: 24px; height: 24px;'></a></div>", unsafe_allow_html=True)

# Display images from Google Drive
drive_files = list_drive_files(json_file_path)
if drive_files:
    st.write("Images in Google Drive:")
    for file in drive_files:
        if 'image' in file['mimeType']:
            img_data = download_from_drive(file['id'], json_file_path)
            img = Image.open(img_data)
            st.image(img, caption=file['name'], use_column_width=True)

            # Add download icon for each image from Google Drive
            img_data = img_data.getvalue()
            st.markdown("<div style='text-align: center;'><a href='javascript:downloadImage(document.querySelector(\".compressed-img:nth-child(" + str(len(uploaded_files) + drive_files.index(file) + 1) + ")\").src, \"" + file['name'] + "\")'><img src='https://image.flaticon.com/icons/png/512/94/94944.png' style='width: 24px; height: 24px;'></a></div>", unsafe_allow_html=True)

            # Add compressed image for each image from Google Drive
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=50)
            img_io.seek(0)
            st.markdown("<img src='data:image/jpeg;base64," + base64.b64encode(img_io.read()).decode() + "' class='compressed-img' style='margin: 5px;'/>", unsafe_allow_html=True)

            # Add rotation functionality for each image from Google Drive
            st.markdown("<div style='text-align: center;'><img src='https://image.flaticon.com/icons/png/512/1151/1151247.png' style='width: 24px; height: 24px;' title='Rotate clockwise' onclick='rotateImage(document.querySelector(\".compressed-img:nth-child(" + str(len(uploaded_files) + drive_files.index(file) + 1) + ")\"), 90)'></div>", unsafe_allow_html=True)

            # Add rotation functionality for each image from Google Drive
            st.markdown("<div style='text-align: center;'><img src='https://image.flaticon.com/icons/png/512/1151/1151250.png' style='width: 24px; height: 24px;' title='Rotate counter-clockwise' onclick='rotateImage(document.querySelector(\".compressed-img:nth-child(" + str(len(uploaded_files) + drive_files.index(file) + 1) + ")\"), -90)'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
