import streamlit as st
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
import qrcode
import base64
import io
import requests
import os
import json
import tempfile


# Initialize Firebase app
# Download the JSON file from the GitHub repository
response = requests.get("https://raw.githubusercontent.com/sagarnr1997/firebase_api/main/imageapp.json")

# Save the JSON content as a dictionary
json_data = json.loads(response.text)

# Check if the default app already exists
try:
    default_app = firebase_admin.get_app()
except ValueError:
    # Use the JSON data to initialize the Firebase app
    cred = credentials.Certificate(json_data)
    firebase_admin.initialize_app(cred, {
        'name': 'Imageapp',  # Add a unique app name
        'storageBucket': 'https://console.firebase.google.com/project/imageapp-d473e/storage/imageapp-d473e.appspot.com/files'
    })

# Initialize Firebase Storage
bucket = storage.bucket()

def upload_image_to_firebase(image_data):
    try:
        # Convert the image data to a base64-encoded string
        image_string = base64.b64encode(image_data.getvalue()).decode('utf-8')

        # Upload the base64-encoded string to Firebase Storage
        blob = bucket.blob("images/" + image_data.name)
        blob.content_type = image_data.type
        blob.upload_from_string(image_string)

        # Get URL of the uploaded image
        return blob.public_url
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def download_image_from_firebase(image_url):
    # Download the image from Firebase Storage using the URL
    response = requests.get(image_url, stream=True)
    response.raise_for_status()
    return response.content

def generate_qr_code(app_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(app_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img

def main():
    st.title('Image Upload and QR Code Generator')

    # Upload image
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        # Display uploaded image
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

        # Upload image to Firebase
        image_url = upload_image_to_firebase(uploaded_file)

        if image_url:
            # Generate and display QR code
            app_url = "https://console.firebase.google.com/project/imageapp-d473e/storage/imageapp-d473e.appspot.com/files"  # Update with your app URL
            qr_img = generate_qr_code(app_url)
            st.image(qr_img, caption='QR Code', use_column_width=True)

    # Display all images in Firebase Storage
    blobs = bucket.list_blobs(prefix="images/")
    cols = st.columns(len(blobs))
    for idx, blob in enumerate(blobs):
        cols[idx].image(blob.public_url, caption=blob.name, use_column_width=True)

    # Face recognition and downloading features
    # For face recognition, you can use a library like OpenCV and implement a face detection model.
    # For downloading,
def display_all_images():
    blobs_iterator = bucket.list_blobs(prefix="images/")
    blobs = list(blobs_iterator)
    
    if not blobs:
        st.write("No images found.")
        return
    
    cols = st.columns(len(blobs))
    download_buttons = []

    for idx, blob in enumerate(blobs):
        cols[idx].image(blob.public_url, caption=blob.name, use_column_width=True)

        # Add a download button for each image
        with cols[idx].form("download_form_{}".format(idx)):
            st.download_button(
                label="Download",
                data=download_image_from_firebase(blob.public_url),
                file_name=blob.name,
                mime="image/{}".format(blob.content_type.split("/")[-1]),
            )
            st.form_submit_button("Submit")

def main():
    st.subheader("All Images")
    display_all_images()

if __name__ == "__main__":
    main()
