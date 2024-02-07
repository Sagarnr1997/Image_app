import streamlit as st
from PIL import Image
import io

# Function to compress image
def compress_image(image, quality=50):
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG', quality=quality)
    img_io.seek(0)
    return img_io

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

        # Compress and provide download links
        st.write("### Download Compressed Images")
        for idx, img in enumerate(uploaded_images):
            compressed_img = compress_image(img)
            st.download_button(
                label=f"Download Image {idx + 1}",
                data=compressed_img,
                file_name=f"compressed_image_{idx + 1}.jpg",
                mime="image/jpeg"
            )

if __name__ == "__main__":
    main()
