import streamlit as st
from PIL import Image

# Function to display uploaded images
def display_images(uploaded_images):
    st.write("## Uploaded Images")
    for img in uploaded_images:
        st.image(img, use_column_width=True)

def main():
    st.title("Image Upload and Display App")

    # Upload multiple images
    st.write("### Upload Images")
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    # Display uploaded images
    if uploaded_files:
        uploaded_images = [Image.open(img) for img in uploaded_files]
        display_images(uploaded_images)

if __name__ == "__main__":
    main()
