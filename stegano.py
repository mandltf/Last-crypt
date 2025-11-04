import streamlit as st
from PIL import Image
import io

# ======== Fungsi Steganografi LSB ========

def encode_image(image, message):
    """Menyembunyikan pesan dalam gambar menggunakan LSB."""
    img = image.convert("RGB")
    
    # 1. Konversi pesan ke biner dan tambahkan penanda akhir
    # Penanda akhir: 1111111111111110 (karakter 'þ')
    binary_msg = ''.join(format(ord(i), '08b') for i in message)
    binary_msg += format(ord('þ'), '016b') 

    msg_index = 0
    
    # Periksa apakah pesan terlalu panjang
    max_bits = img.size[0] * img.size[1] * 3
    if len(binary_msg) > max_bits:
        raise ValueError("Pesan terlalu panjang untuk disembunyikan dalam gambar ini.")
        
    width, height = img.size
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            if msg_index < len(binary_msg):
                r, g, b = pixels[x, y]
                
                # Sembunyikan bit di saluran Merah (R)
                r = (r & ~1) | int(binary_msg[msg_index])
                msg_index += 1
                
                # Sembunyikan bit di saluran Hijau (G)
                if msg_index < len(binary_msg):
                    g = (g & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                
                # Sembunyikan bit di saluran Biru (B)
                if msg_index < len(binary_msg):
                    b = (b & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                
                pixels[x, y] = (r, g, b)
            else:
                return img
    return img


def decode_image(image):
    """Mengambil pesan tersembunyi dari gambar."""
    img = image.convert("RGB")
    width, height = img.size
    pixels = img.load()

    binary_msg = ""
    
    # 1. Ekstrak bit LSB dari setiap channel
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_msg += str(r & 1)
            binary_msg += str(g & 1)
            binary_msg += str(b & 1)

    # 2. Konversi bit biner ke karakter
    all_bytes = [binary_msg[i:i+8] for i in range(0, len(binary_msg), 8)]
    decoded_msg = ""
    
    for byte in all_bytes:
        # Hanya proses byte 8-bit penuh
        if len(byte) == 8:
            decoded_msg += chr(int(byte, 2))
            # Cek penanda akhir pesan (karakter 'þ' memiliki kode ASCII 254)
            if decoded_msg.endswith("þ"):  
                break
                
    # 3. Hapus karakter penanda akhir ('þ')
    return decoded_msg[:-1]


# ======== Aplikasi Streamlit ========

st.set_page_config(page_title="LSB Steganografi", page_icon="🕵️‍♀️", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .stButton>button {
        color: #0d1117;
        background-color: #58a6ff;
        border-radius: 8px;
        border: 1px solid #58a6ff;
    }
    .stRadio > div {
        background-color: #21262d;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


st.title("🕵️‍♀️ LSB Steganography Tool")
st.subheader("Sembunyikan dan Ambil Pesan Rahasia di Dalam Gambar")

menu = st.radio("Pilih Mode Operasi:", 
                ["🔐 Encode (Sembunyikan Pesan)", "🔎 Decode (Ambil Pesan)"],
                horizontal=True)

st.divider()

if menu == "🔐 Encode (Sembunyikan Pesan)":
    st.markdown("### 🖼️ Sembunyikan Pesan (Encode)")
    uploaded_file = st.file_uploader("1. Upload Gambar Asli (PNG direkomendasikan)", type=["png", "jpg", "jpeg"])
    message = st.text_area("2. Masukkan Pesan Rahasia:", max_chars=1000)

    if uploaded_file and message:
        try:
            image = Image.open(uploaded_file)
            
            # Tampilkan gambar asli
            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption="Gambar Asli", use_container_width=True)
                st.info(f"Dimensi: {image.size[0]}x{image.size[1]} pixels.")
            
            # Lakukan Encoding
            encoded_img = encode_image(image, message)
            
            # Simpan ke buffer agar bisa diunduh
            buf = io.BytesIO()
            encoded_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            with col2:
                st.image(encoded_img, caption="Hasil Gambar Terenkripsi (Download dalam format PNG)", use_container_width=True)
                st.success("Encoding Selesai!")
                
                # Tautan Download
                st.download_button(
                    label="💾 Download Gambar Hasil Encode (.png)", 
                    data=byte_im, 
                    file_name="encoded_stegano_image.png", 
                    mime="image/png"
                )
                st.warning("Pastikan Anda mengunduh dan membagikan gambar dalam format **PNG** untuk menjaga pesan tersembunyi.")
            
        except ValueError as e:
            st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

elif menu == "🔎 Decode (Ambil Pesan)":
    st.markdown("### 🔓 Ambil Pesan (Decode)")
    uploaded_file = st.file_uploader("1. Upload Gambar yang Berisi Pesan Rahasia (Hasil Encode)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            
            st.image(image, caption="Gambar untuk di Decode", use_container_width=True)
            
            # Lakukan Decoding
            with st.spinner('Mencari pesan tersembunyi...'):
                decoded_message = decode_image(image)
            
            if decoded_message:
                st.success("✅ Pesan tersembunyi ditemukan:")
                st.code(decoded_message, language='text')
            else:
                st.warning("Pesan tersembunyi tidak ditemukan atau gambar tidak mengandung pesan LSB yang valid.")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan saat decoding: {e}")

