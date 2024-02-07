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

# Initialize Firebase app
cred = credentials.Certificate(response)
firebase_app = initialize_app(cred)
bucket = storage.bucket(app=firebase_app)

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
