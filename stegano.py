import streamlit as st
from PIL import Image
import io

# ======== Fungsi Steganografi LSB ========

def encode_image(image, message):
    img = image.convert("RGB")
    width, height = img.size
    pixels = img.load()

    binary_msg = ''.join(format(ord(i), '08b') for i in message)
    binary_msg += '1111111111111110'  # penanda akhir pesan

    msg_index = 0
    for y in range(height):
        for x in range(width):
            if msg_index < len(binary_msg):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_msg[msg_index])
                msg_index += 1
                if msg_index < len(binary_msg):
                    g = (g & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                if msg_index < len(binary_msg):
                    b = (b & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                pixels[x, y] = (r, g, b)
            else:
                return img
    return img


def decode_image(image):
    img = image.convert("RGB")
    width, height = img.size
    pixels = img.load()

    binary_msg = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_msg += str(r & 1)
            binary_msg += str(g & 1)
            binary_msg += str(b & 1)

    all_bytes = [binary_msg[i:i+8] for i in range(0, len(binary_msg), 8)]
    decoded_msg = ""
    for byte in all_bytes:
        decoded_msg += chr(int(byte, 2))
        if decoded_msg.endswith("þ"):  # karakter penanda akhir
            break
    return decoded_msg[:-1]


# ======== Aplikasi Streamlit ========

st.title("🕵️‍♀️ Aplikasi Steganografi LSB")
st.write("Sembunyikan dan ambil pesan rahasia dari gambar!")

menu = st.radio("Pilih mode:", ["🔐 Encode (Sembunyikan Pesan)", "🔎 Decode (Ambil Pesan)"])

if menu == "🔐 Encode (Sembunyikan Pesan)":
    uploaded_file = st.file_uploader("Upload gambar (PNG atau JPG)", type=["png", "jpg", "jpeg"])
    message = st.text_area("Masukkan pesan rahasia:")

    if uploaded_file and message:
        image = Image.open(uploaded_file)
        encoded_img = encode_image(image, message)
        
        # Simpan ke buffer agar bisa diunduh
        buf = io.BytesIO()
        encoded_img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.image(encoded_img, caption="Hasil gambar dengan pesan tersembunyi", use_column_width=True)
        st.download_button(label="💾 Download gambar hasil", data=byte_im, file_name="encoded_image.png", mime="image/png")

elif menu == "🔎 Decode (Ambil Pesan)":
    uploaded_file = st.file_uploader("Upload gambar yang berisi pesan rahasia", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        decoded_message = decode_image(image)
        st.success("Pesan tersembunyi ditemukan:")
        st.code(decoded_message)
