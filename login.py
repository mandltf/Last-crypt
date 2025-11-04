import streamlit as st
from koneksi import connect_db
import hashlib
import base64
import mysql.connector
from mysql.connector import Error
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


# -------------------- Hash & AES --------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def aes_encrypt(text: str, key_bytes: bytes) -> str:
    cipher = AES.new(key_bytes, AES.MODE_EAX)
    ct, tag = cipher.encrypt_and_digest(text.encode())
    payload = cipher.nonce + ct
    return base64.b64encode(payload).decode()

def aes_decrypt(payload_b64: str, key_bytes: bytes) -> str:
    data = base64.b64decode(payload_b64)
    nonce, ct = data[:16], data[16:]
    cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ct).decode()


# -------------------- Register & Login --------------------
def register_user_db(name: str, password: str, phone: str):
    conn = connect_db()
    if not conn:
        return False, "Gagal koneksi DB."
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE name=%s", (name,))
    if cur.fetchone():
        conn.close()
        return False, "Nama sudah terdaftar."

    pw_hash = hash_password(password)
    aes_key = get_random_bytes(16)
    encrypted_phone = aes_encrypt(phone, aes_key)
    cur.execute(
        "INSERT INTO users (name, password_hash, phone_encrypted, aes_key) VALUES (%s,%s,%s,%s)",
        (name, pw_hash, encrypted_phone, aes_key.hex())
    )
    conn.commit()
    conn.close()
    return True, "Registrasi berhasil!"

def login_user_db(name: str, password: str):
    conn = connect_db()
    if not conn:
        return False, "Gagal koneksi DB."
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, phone_encrypted, aes_key FROM users WHERE name=%s", (name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "Nama tidak ditemukan."

    uid, pw_hash, phone_enc, aes_key_hex = row
    if pw_hash != hash_password(password):
        return False, "Password salah."

    try:
        key_bytes = bytes.fromhex(aes_key_hex)
        phone = aes_decrypt(phone_enc, key_bytes)
    except Exception as e:
        return False, f"Gagal dekripsi nomor: {e}"
    return True, {"user_id": uid, "phone": phone}

# -------------------- Halaman Streamlit --------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

def login_page():
    st.title("🔐 Login Sistem Kriptografi")
    name = st.text_input("Nama Lengkap")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        ok, res = login_user_db(name, password)
        if ok:
            st.session_state.logged_in = True
            st.session_state.name = name
            st.session_state.user_id = res["user_id"]
            st.session_state.phone = res["phone"]
            st.session_state.page = "dashboard" 
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error(res)

    st.write("---")
    if st.button("Daftar Akun Baru"):
        st.session_state.page = "register"
        st.rerun()

def register_page():
    st.title("📝 Register Pengguna Baru")
    name = st.text_input("Nama Lengkap")
    phone = st.text_input("Nomor Telepon")
    password = st.text_input("Password", type="password")
    if st.button("Daftar"):
        if not (name and phone and password):
            st.warning("Semua kolom wajib diisi!")
        else:
            ok, msg = register_user_db(name, password, phone)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
    st.write("---")
    if st.button("Kembali ke Login"):
        st.session_state.page = "login"
        st.rerun()
    