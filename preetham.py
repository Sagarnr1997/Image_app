import streamlit as st
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage, initialize_app
import qrcode
import base64
import io
import requests
import os
import json
import tempfile


# Initialize Firebase app
response = requests.get("https://raw.githubusercontent.com/sagarnr1997/firebase_api/main/imageapp.json")
json_data = json.loads(response.text)

try:
    default_app = initialize_app(credentials.Certificate(json_data), {
        'name': 'Imageapp',
        'storageBucket': 'gs://preetham-c1ae2.appspot.com'
    })
    bucket = storage.bucket(app=default_app)
except ValueError as e:
    st.error(f"Failed to initialize Firebase app: {str(e)}")

def display_all_images():
    try:
        blobs_iterator = bucket.list_blobs()
        blobs = list(blobs_iterator)
        
        if not blobs:
            st.write("No images found.")
            return
        
        for idx, blob in enumerate(blobs):
            st.write(f"Image URL {idx + 1}: {blob.public_url}")
            st.image(blob.public_url, caption=blob.name, use_column_width=True)
    except NameError as e:
        st.error("Firebase bucket is not defined. Make sure the app is initialized correctly.")

def main():
    st.title('All Images in Firebase Storage')

    # Display all images in Firebase Storage
    display_all_images()

if __name__ == "__main__":
    main()
