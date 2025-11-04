import streamlit as st
from Crypto.Cipher import Salsa20

# ===== Caesar Cipher =====
def caesar_encrypt(text, shift):
    hasil = ""
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            hasil += chr((ord(char) - start + shift) % 26 + start)
        else:
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


# ======= Streamlit App ========
st.title("🔐 Super Enkripsi Data (Caesar + Salsa20)")

st.write("Form input data pribadi lalu terenkripsi menggunakan Caesar Cipher + Salsa20")

with st.form("form_data"):
    nik = st.text_input("NIK")
    alamat = st.text_area("Alamat")

    agama = st.selectbox("Agama", ["Islam", "Kristen", "Katolik", "Hindu", "Buddha", "Konghucu"])
    goldar = st.selectbox("Golongan Darah", ["A", "B", "AB", "O"])

    shift = st.number_input("Shift Caesar (angka)", min_value=1, max_value=25, value=3)
    key = st.text_input("Kunci Salsa20 (16 karakter)").encode()

    submitted = st.form_submit_button("🔒 Enkripsi & 🔓 Dekripsi")


if submitted:
    if len(key) != 16:
        st.error("❌ Kunci Salsa20 harus 16 karakter!")
    else:
        # Encrypt
        enc_nik = super_encrypt(nik, shift, key)
        enc_alamat = super_encrypt(alamat, shift, key)

        # Convert to hex for display
        enc_nik_hex = enc_nik.hex()
        enc_alamat_hex = enc_alamat.hex()

        # Decrypt for verification
        dec_nik = super_decrypt(enc_nik, shift, key)
        dec_alamat = super_decrypt(enc_alamat, shift, key)

        st.success("✅ Data berhasil dienkripsi!")

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
            "Alamat terenkripsi": enc_alamat_hex
        })

        st.subheader("🔓 Hasil Dekripsi (Verifikasi)")
        st.write({
            "Dekripsi NIK": dec_nik,
            "Dekripsi Alamat": dec_alamat
        })