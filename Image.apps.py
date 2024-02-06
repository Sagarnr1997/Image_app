# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 21:56:00 2024

@author: Sagar NR
"""

import streamlit as st
from PIL import Image
import qrcode
import os

UPLOAD_DIRECTORY = "uploads"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Function to reduce image size
def reduce_image_size(image, max_width=800):
    width, height = image.size
    if width > max_width:
        ratio = max_width / width
        new_width = max_width
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height))
    return image

# Function to generate and save QR code
def generate_qr_code(image_filename):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(f"https://yourwebsite.com/download_image/{image_filename}")
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(UPLOAD_DIRECTORY, f"qr_{image_filename}.png")
    qr_image.save(qr_path)
    return qr_path

def main():
    st.title('Image Resizer and QR Code Generator')

    # Upload multiple images
    uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            # Save uploaded image
            image_path = os.path.join(UPLOAD_DIRECTORY, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            # Display uploaded image
            st.image(image_path, caption=f'Uploaded Image: {uploaded_file.name}', use_column_width=True)

            # Reduce image size
            image = Image.open(image_path)
            reduced_image = reduce_image_size(image)

            # Display reduced image
            st.image(reduced_image, caption='Reduced Image', use_column_width=True)

            # Generate and display QR code
            qr_path = generate_qr_code(uploaded_file.name)
            st.image(qr_path, caption=f'Scan QR Code to Download: {uploaded_file.name}', use_column_width=True)

if __name__ == "__main__":
    main()
