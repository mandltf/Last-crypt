import streamlit as st
from PIL import Image
import io
from koneksi import connect_db
from mysql.connector import Error

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

# -------------------- Simpan Steganografi Data --------------------
def save_stegano_record(user_id: int, original_file_name: str, stegan_image_bytes: bytes, hidden_message: str):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO data_stegano (user_id, original_image_name, stegan_image_data, hidden_message)
            VALUES (%s, %s, %s, %s)
        """, (user_id, original_file_name, stegan_image_bytes, hidden_message))
        conn.commit()
        return True
    except Error as e:
        st.error(f"Gagal menyimpan data steganografi ke DB: {e}")
        # Note: Jika error 1153 muncul lagi, Anda harus menaikkan 'max_allowed_packet' di konfigurasi MySQL.
        return False
    finally:
        if conn:
            conn.close()

# ======== Aplikasi Streamlit ========
def stegano():
    st.title("🕵️‍♀️ Aplikasi Steganografi LSB")
    st.write("Masukkan foto ktp atau foto diri anda!")

    # Cek Login dan NIK
    if 'user_id' not in st.session_state:
        st.error("⚠️ Anda harus login untuk menggunakan fitur ini.")
        return
    
    # Ambil NIK dari Superteks
    nik_for_stegano = st.session_state.get('nik_original', None)
    
    menu = st.radio("Pilih Mode Operasi:", ["🔐 Encode (Sembunyikan Pesan)", "🔎 Decode (Ambil Pesan)"], horizontal=True)

    st.divider()

    if menu == "🔐 Encode (Sembunyikan Pesan)":
        st.markdown("### 🖼️ Sembunyikan Pesan (Encode)")
        
        # --- Bagian Pesan Otomatis dari NIK ---
        if nik_for_stegano:
            st.info(f"NIK dari Super Enkripsi (**{nik_for_stegano}**) akan **otomatis** digunakan sebagai pesan rahasia.")
            hidden_message = nik_for_stegano
            st.text_area("Pesan Rahasia Otomatis (NIK):", value=hidden_message, disabled=True)
        else:
            st.warning("⚠️ NIK dari 'Super Enkripsi Teks' belum tersedia di sesi. Pesan rahasia harus diinput manual.")
            hidden_message = st.text_area("2. Masukkan Pesan Rahasia:", max_chars=1000)
            
        # --- Bagian Upload ---
        uploaded_file = st.file_uploader("1. Upload Gambar Asli (PNG direkomendasikan)", type=["png", "jpg", "jpeg"])
        
        if uploaded_file and hidden_message:
            try:
                image = Image.open(uploaded_file)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.image(image, caption="Gambar Asli", use_container_width=True)
                    
                # Lakukan Encoding
                encoded_img = encode_image(image, hidden_message)
                
                # Simpan ke buffer agar bisa diunduh
                buf = io.BytesIO()
                encoded_img.save(buf, format="PNG")
                byte_im = buf.getvalue() # Data biner gambar hasil encode
                
                with col2:
                    st.image(encoded_img, caption="Hasil Gambar Terenkripsi", use_container_width=True)
                    st.success("Encoding Selesai!")
                    
                    # Tautan Download
                    st.download_button(
                        label="💾 Download Gambar Hasil Encode (.png)", 
                        data=byte_im, 
                        file_name=f"stegan_NIK_{st.session_state.user_id}.png", 
                        mime="image/png"
                    )

                    # --- Simpan ke Database ---
                    saved = save_stegano_record(st.session_state.user_id, uploaded_file.name, byte_im, hidden_message)
                    if saved:
                        st.success("✅ Gambar berhasil di-encode dan **disimpan ke database**!")
                    else:
                        st.error("❌ Gagal menyimpan gambar steganografi ke database.")

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
                    
                    if nik_for_stegano and decoded_message == nik_for_stegano:
                        st.success("✨ Pesan yang ditemukan **cocok** dengan NIK Anda yang tersimpan di sesi.")
                    elif nik_for_stegano:
                        st.warning(f"⚠️ Pesan yang ditemukan **TIDAK COCOK** dengan NIK sesi Anda (`{nik_for_stegano}`).")
                else:
                    st.warning("Pesan tersembunyi tidak ditemukan atau gambar tidak mengandung pesan LSB yang valid.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan saat decoding: {e}")
