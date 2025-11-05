import streamlit as st
import base64
import mysql.connector
from mysql.connector import Error
from Crypto.Random import get_random_bytes
from koneksi import connect_db

# simpan ke db
def save_file_record(user_id: int, original_name: str, encrypted_b64: str, XOR_key: str):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO data_encrypted (user_id, data_type, original_name, encrypted_data, XOR_key)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, "file", original_name, encrypted_b64, XOR_key))
    conn.commit()
    conn.close()
    return True

# XOR
def xor_bytes(data: bytes, key: str) -> bytes:
    kb = key.encode()
    return bytes([b ^ kb[i % len(kb)] for i, b in enumerate(data)])

def file_encrypt():
    st.title("📁 Enkripsi & Dekripsi File PDF / TXT (XOR)")
    st.write(f"Login sebagai: **{st.session_state.name}** | No. Telepon: `{st.session_state.phone}`")

    uploaded = st.file_uploader("Pilih file (.pdf atau .txt)", type=["pdf", "txt"])
    key = st.text_input("Masukkan kunci XOR")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔒 Enkripsi File"):
            if not uploaded or not key:
                st.warning("Pilih file dan isi kunci!")
            else:
                data = uploaded.read()
                result = xor_bytes(data, key)
                b64 = base64.b64encode(result).decode()
                saved = save_file_record(st.session_state.user_id, uploaded.name, b64, key)
                if saved:
                    st.success("File terenkripsi dan disimpan.")
                    st.download_button("Download Encrypted File", data=result, file_name=f"enc_{uploaded.name}")
                else:
                    st.error("Gagal menyimpan ke DB.")

    with col2:
        if st.button("🔓 Dekripsi File"):
            if not uploaded or not key:
                st.warning("Pilih file dan isi kunci!")
            else:
                data = uploaded.read()
                result = xor_bytes(data, key)
                st.success("File berhasil didekripsi.")
                st.download_button("Download Decrypted File", data=result, file_name=f"dec_{uploaded.name}")
