import streamlit as st
from Crypto.Cipher import Salsa20
from mysql.connector import Error
from koneksi import connect_db

# ===== Caesar Cipher =====
def caesar_encrypt(text, shift):
    hasil = ""
    for char in text:
        if char.isalpha():
            # Enkripsi Abjad (A-Z, a-z)
            start = ord('A') if char.isupper() else ord('a')
            hasil += chr((ord(char) - start + shift) % 26 + start)
        elif char.isdigit():
            # Enkripsi Angka (0-9)
            start = ord('0')
            hasil += chr((ord(char) - start + shift) % 10 + start)
        else:
            # Karakter lain (spasi, simbol, dll.) tidak dienkripsi
            hasil += char
    return hasil

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

# ===== Salsa20 Encryption =====
def salsa20_encrypt(data, key):
    cipher = Salsa20.new(key=key)
    ciphertext = cipher.nonce + cipher.encrypt(data.encode('utf-8'))
    return ciphertext

def salsa20_decrypt(ciphertext, key):
    nonce = ciphertext[:8]
    cipher = Salsa20.new(key=key, nonce=nonce)
    return cipher.decrypt(ciphertext[8:]).decode('utf-8')

# ===== Super Encryption =====
def super_encrypt(pesan, shift, key):
    hasil_caesar = caesar_encrypt(pesan, shift)
    hasil_salsa = salsa20_encrypt(hasil_caesar, key)
    return hasil_salsa

def super_decrypt(ciphertext, shift, key):
    hasil_salsa = salsa20_decrypt(ciphertext, key)
    hasil_caesar = caesar_decrypt(hasil_salsa, shift)
    return hasil_caesar

# -------------------- Simpan Enkripsi Data Pribadi --------------------
def save_super_encryption_data(user_id: int, enc_nik_hex: str, enc_alamat_hex: str, agama: str, goldar: str, shift: int, key_hex: str):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO data_pribadi_enkripsi (user_id, nik_encrypted, alamat_encrypted, agama, golongan_darah, caesar_shift, salsa20_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, enc_nik_hex, enc_alamat_hex, agama, goldar, shift, key_hex))
        conn.commit()
        return True
    except Error as e:
        st.error(f"Gagal menyimpan data ke DB: {e}")
        return False
    finally:
        if conn:
            conn.close()

# ======= Streamlit App ========
def supertext():
    st.title("🔐 Super Enkripsi Data (Caesar + Salsa20)")

    st.write("Form input data pribadi lalu terenkripsi menggunakan Caesar Cipher + Salsa20")

    with st.form("form_data"):
        nik = st.text_input("NIK")
        alamat = st.text_area("Alamat")

        agama = st.selectbox("Agama", ["Islam", "Kristen", "Katolik", "Hindu", "Buddha", "Konghucu"])
        goldar = st.selectbox("Golongan Darah", ["A", "B", "AB", "O"])

        shift = st.number_input("Shift Caesar (angka)", min_value=1, max_value=25, value=3)
        key_input = st.text_input("Kunci Salsa20 (16 karakter)")
        key = key_input.encode()

        submitted = st.form_submit_button("🔒 Enkripsi & 🔓 Dekripsi")


    if submitted:
        if len(key) != 16:
            st.error("❌ Kunci Salsa20 harus 16 karakter!")
        else:
            # Encrypt
            enc_nik = super_encrypt(nik, shift, key)
            enc_alamat = super_encrypt(alamat, shift, key)

            # Convert to hex for display and storage
            enc_nik_hex = enc_nik.hex()
            enc_alamat_hex = enc_alamat.hex()
            key_hex = key.hex() 

            # Decrypt for verification
            dec_nik = super_decrypt(enc_nik, shift, key)
            dec_alamat = super_decrypt(enc_alamat, shift, key)

            # --- Simpan ke Database ---
            user_id = st.session_state.user_id # Ambil user_id dari session
            saved = save_super_encryption_data(user_id, enc_nik_hex, enc_alamat_hex, agama, goldar, shift, key_hex)

            if saved:
                st.success("✅ Data berhasil dienkripsi dan **disimpan ke database**!")
            else:
                st.error("❌ Data berhasil dienkripsi, tetapi **gagal disimpan ke database**! Cek pesan error di atas.")

            st.subheader("📦 Data Asli")
            st.write({
                "NIK": nik,
                "Alamat": alamat,
                "Agama": agama,
                "Golongan Darah": goldar
            })

            st.subheader("🔐 Data Terenkripsi (Hex)")
            st.write({
                "NIK terenkripsi": enc_nik_hex,
                "Alamat terenkripsi": enc_alamat_hex,
                "Kunci Salsa20 (Hex)": key_hex,
                "Shift Caesar": shift
            })

            st.subheader("🔓 Hasil Dekripsi (Verifikasi)")
            st.write({
                "Dekripsi NIK": dec_nik,
                "Dekripsi Alamat": dec_alamat
            })