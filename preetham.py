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

response = requests.get("https://raw.githubusercontent.com/sagarnr1997/firebase_api/main/imageapp.json")

# Save the JSON content as a dictionary
json_data = json.loads(response.text)

try:
    default_app = firebase_admin.get_app()
except ValueError:
    # Use the JSON data to initialize the Firebase app
    cred = credentials.Certificate(json_data)
    firebase_admin.initialize_app(cred, {
        'name': 'Imageapp',  # Add a unique app name
        'storageBucket': 'imageapp-d473e.appspot.com'
    })

# Initialize Firebase Storage
bucket = storage.bucket()

def display_all_images():
    blobs_iterator = bucket.list_blobs(prefix="images/")
    blobs = list(blobs_iterator)
    
    if not blobs:
        st.write("No images found.")
        return
    
    for blob in blobs:
        st.image(blob.public_url, caption=blob.name, use_column_width=True)

def main():
    st.title('All Images in Firebase Storage')

    # Display all images in Firebase Storage
    display_all_images()

if __name__ == "__main__":
    main()
