import streamlit as st
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
import requests
import json
import base64

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
        'storageBucket': 'imageapp-d473e.appspot.com'
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
            qr_code_url = f"https://storage.googleapis.com/imageapp-d473e.appspot.com/images/{image_url}" # Update with your URL structure
            st.image(qr_code_url, caption='QR Code', use_column_width=True)
        else:
            st.error("Failed to upload image to Firebase.")

if __name__ == "__main__":
    main()
