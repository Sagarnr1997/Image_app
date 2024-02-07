import streamlit as st
from PIL import Image
import io

# JavaScript function for client-side image resizing and compression
js_code = """
<script>
function compressAndUpload(files) {
    var compressedFiles = [];
    var maxSize = 1024; // Maximum file size in KB

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var fileName = file.name;
        var reader = new FileReader();

        reader.onload = function(event) {
            var img = new Image();
            img.src = event.target.result;

            img.onload = function() {
                var canvas = document.createElement('canvas');
                var ctx = canvas.getContext('2d');
                var maxWidth = 800; // Maximum width for the image
                var maxHeight = 600; // Maximum height for the image
                var ratio = 1;

                if (img.width > maxWidth) {
                    ratio = maxWidth / img.width;
                } else if (img.height > maxHeight) {
                    ratio = maxHeight / img.height;
                }

                canvas.width = img.width * ratio;
                canvas.height = img.height * ratio;
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                canvas.toBlob(function(blob) {
                    var compressedFile = new File([blob], fileName, {type: 'image/jpeg'});
                    compressedFiles.push(compressedFile);

                    if (compressedFiles.length === files.length) {
                        uploadCompressedFiles(compressedFiles);
                    }
                }, 'image/jpeg', 0.7); // Compression quality (0.7 is 70%)
            }
        };

        reader.readAsDataURL(file);
    }
}

function uploadCompressedFiles(files) {
    var formData = new FormData();

    for (var i = 0; i < files.length; i++) {
        formData.append('file', files[i]);
    }

    // You can perform an AJAX request to upload the compressed files
    // Example: Use fetch() or XMLHttpRequest to send formData to your server
    // fetch('/upload', {
    //     method: 'POST',
    //     body: formData
    // })
    // .then(response => {
    //     console.log('Upload complete!');
    // });

    console.log('Compressed files ready for upload:', files);
}
</script>
"""

# Function to compress image
def compress_image(image, quality=50):
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG', quality=quality)
    img_io.seek(0)
    return img_io

def main():
    st.title("Mobile Gallery and Selection")

    # Display the JavaScript code in the Streamlit app
    st.write(js_code, unsafe_allow_html=True)

    # Upload images and call the JavaScript function when files are selected
    st.write("Upload Images")
    uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        uploaded_images = [Image.open(img) for img in uploaded_files]

        # Display images in a mobile gallery format
        st.write("<style> .gallery { display: flex; flex-wrap: wrap; } .gallery img { width: 100px; height: 100px; object-fit: cover; margin: 5px; cursor: pointer; } </style>", unsafe_allow_html=True)
        st.write("<div class='gallery'>")
        for idx, img in enumerate(uploaded_images):
            # Compress the image
            compressed_img = compress_image(img)

            # Display the image with a checkbox for selection
            st.write(f"<label for='img_{idx}'><img id='img_{idx}' src='data:image/png;base64,{compressed_img}' /></label><br>", unsafe_allow_html=True)

        st.write("</div>")
        
        # Download button for selected images
        if st.button("Download Selected Images"):
            selected_images = []
            for idx, img in enumerate(uploaded_images):
                checkbox_val = st.checkbox(f"Select Image {idx + 1}", key=f"checkbox_{idx}")
                if checkbox_val:
                    selected_images.append(img)

            for idx, img in enumerate(selected_images):
                # Compress the image
                compressed_img = compress_image(img)

                # Download the compressed image
                st.download_button(
                    label=f"Download Image {idx + 1}",
                    data=compressed_img,
                    file_name=f"compressed_image_{idx + 1}.jpg",
                    mime="image/jpeg"
                )

if __name__ == "__main__":
    main()
