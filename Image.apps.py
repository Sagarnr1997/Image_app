# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 21:56:00 2024

@author: Sagar NR
"""

import streamlit as st
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase
cred = credentials.Certificate("https://raw.githubusercontent.com/Sagarnr1997/Image_app/main/imageapp.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://imageapp-d473e.appspot.com'
})
bucket = storage.bucket()

# Function to upload image to Firebase Storage
def upload_image_to_firebase(image_data):
    # Upload image to Firebase Storage
    blob = bucket.blob("images/" + image_data.name)
    blob.upload_from_string(image_data.read(), content_type=image_data.type)

    # Get URL of the uploaded image
    return blob.public_url

def main():
    st.title('Image Upload and QR Code Generator')

    # Upload image
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        # Resize image
        image = Image.open(uploaded_file)
        resized_image = image.resize((200, 200))  # Adjust the size as per your requirement

        # Display resized image
        st.image(resized_image, caption='Uploaded Image', use_column_width=True)

        # Upload image to Firebase
        image_url = upload_image_to_firebase(uploaded_file)

        # Generate and display QR code
        qr_code_url = f"https://yourapp.com/image/{image_url}"  # Adjust URL structure as needed
        st.image(qr_code_url, caption='QR Code', use_column_width=True)

if __name__ == "__main__":
    main()
