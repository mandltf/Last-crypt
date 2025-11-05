import streamlit as st
from PIL import Image
import io
from koneksi import connect_db
from mysql.connector import Error
import super_enkrip as se 

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

# -------------------- Ambil dan Dekripsi NIK dari DB --------------------
def get_and_decrypt_nik(user_id: int):
    """Mengambil NIK terenkripsi, shift, dan key dari DB, lalu mendekripsi NIK."""
    conn = connect_db()
    if not conn:
        return None, "Gagal koneksi ke database."
    cur = conn.cursor()
    try:
        # Ambil record enkripsi teks terbaru milik user ini
        cur.execute("""
            SELECT nik_encrypted, caesar_shift, salsa20_key
            FROM data_pribadi_enkripsi
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        result = cur.fetchone()
        
        if result:
            enc_nik_hex, shift, key_hex = result
            
            # Konversi kembali ke bytes dari hex
            enc_nik = bytes.fromhex(enc_nik_hex)
            key_bytes = bytes.fromhex(key_hex)
            
            # Dekripsi NIK
            decrypted_nik = se.super_decrypt(enc_nik, shift, key_bytes)
            return decrypted_nik, None
        else:
            return None, "Tidak ditemukan data NIK terenkripsi untuk user ini."
            
    except Error as e:
        return None, f"Gagal mengambil data dari DB: {e}"
    except Exception as e:
        return None, f"Gagal dekripsi NIK: Pastikan modul 'super_enkrip' sudah diimpor dan berfungsi: {e}"
    finally:
        if conn:
            conn.close()


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
        return False
    finally:
        if conn:
            conn.close()

# ======== Aplikasi Streamlit ========
def stegano():
    st.title("🕵️‍♀️ Aplikasi Steganografi LSB")
    st.write("Masukkan foto ktp atau foto diri anda!")

    # Cek Login
    if 'user_id' not in st.session_state:
        st.error("⚠️ Anda harus login untuk menggunakan fitur ini.")
        return

    # Ambil NIK dari Database
    # Jalankan hanya sekali saat halaman diakses/direfresh
    if 'nik_decrypted' not in st.session_state:
        with st.spinner('Mengambil dan mendekripsi NIK terbaru dari database...'):
            decrypted_nik, error = get_and_decrypt_nik(st.session_state.user_id)
        if error:
            st.session_state['nik_decrypted'] = None
            st.session_state['nik_error'] = error
        else:
            st.session_state['nik_decrypted'] = decrypted_nik
            st.session_state['nik_error'] = None

    nik_for_stegano = st.session_state.get('nik_decrypted')
    nik_error = st.session_state.get('nik_error')

    menu = st.radio("Pilih Mode Operasi:", ["🔐 Encode (Sembunyikan Pesan)", "🔎 Decode (Ambil Pesan)"], horizontal=True)

    st.divider()

    if menu == "🔐 Encode (Sembunyikan Pesan)":
        st.markdown("### 🖼️ Sembunyikan Pesan (Encode)")

        # --- Bagian Pesan Otomatis dari NIK ---
        if nik_for_stegano:
            st.info(f"NIK terbaru yang didekripsi dari DB (**{nik_for_stegano}**) akan otomatis digunakan.")
            hidden_message = nik_for_stegano
            st.text_area("Pesan Rahasia Otomatis (NIK):", value=hidden_message, disabled=True)
        elif nik_error:
            st.error(f"⚠️ Gagal mengambil NIK dari DB: {nik_error}")
            hidden_message = st.text_area("Masukkan Pesan Rahasia", max_chars=1000)
        else:
            st.warning("⚠️ NIK belum ditemukan. Masukkan pesan manual.")
            hidden_message = st.text_area("Masukkan Pesan Rahasia", max_chars=1000)

        uploaded_file = st.file_uploader("Upload Gambar Asli (PNG direkomendasikan)", type=["png", "jpg", "jpeg"])

        if uploaded_file and hidden_message:
            try:
                image = Image.open(uploaded_file)

                col1, col2 = st.columns(2)
                with col1:
                    st.image(image, caption="Gambar Asli", use_container_width=True)

                # Encode
                encoded_img = encode_image(image, hidden_message)
                buf = io.BytesIO()
                encoded_img.save(buf, format="PNG")
                byte_im = buf.getvalue()

                with col2:
                    st.image(encoded_img, caption="Hasil Encode", use_container_width=True)
                    st.success("Encoding selesai!")

                    st.download_button(
                        label="💾 Download Gambar",
                        data=byte_im,
                        file_name=f"stegan_{st.session_state.user_id}.png",
                        mime="image/png"
                    )

                    saved = save_stegano_record(st.session_state.user_id, uploaded_file.name, byte_im, hidden_message)
                    if saved:
                        st.success("✅ Disimpan ke database!")
            except Exception as e:
                st.error(f"Error: {e}")

    elif menu == "🔎 Decode (Ambil Pesan)":
        st.markdown("### 🔓 Ambil Pesan")

        uploaded_file = st.file_uploader("Upload Gambar yang Berisi Pesan", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Gambar Decode", use_container_width=True)

                with st.spinner('Mencari pesan...'):
                    decoded_message = decode_image(image)

                if decoded_message:
                    st.success("✅ Pesan ditemukan:")
                    st.code(decoded_message)

                    if nik_for_stegano and decoded_message == nik_for_stegano:
                        st.success("✅ Pesan cocok dengan NIK anda.")
                    elif nik_for_stegano:
                        st.warning("⚠️ Pesan TIDAK cocok dengan NIK anda.")
                else:
                    st.warning("Tidak ditemukan pesan tersembunyi.")
            except Exception as e:
                st.error(f"Error: {e}")
