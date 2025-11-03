import streamlit as st
import hashlib
import base64
import mysql.connector
from mysql.connector import Error
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# ---------------- DB CONFIG ----------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""  # sesuaikan
DB_NAME = "kriptografi"

# ---------------- DB CONNECT ----------------
def connect_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        return conn
    except Error as e:
        st.error(f"DB connection error: {e}")
        return None

# ---------------- UTIL: HASH ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- AES (untuk NIK) ----------------
def aes_encrypt_nik(text: str, key_bytes: bytes) -> str:
    cipher = AES.new(key_bytes, AES.MODE_EAX)
    ct, tag = cipher.encrypt_and_digest(text.encode())
    payload = cipher.nonce + ct
    return base64.b64encode(payload).decode()

def aes_decrypt_nik(payload_b64: str, key_bytes: bytes) -> str:
    data = base64.b64decode(payload_b64)
    nonce, ct = data[:16], data[16:]
    cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ct).decode()

# ---------------- XOR (file) ----------------
def xor_bytes(data: bytes, key: str) -> bytes:
    kb = key.encode()
    return bytes([b ^ kb[i % len(kb)] for i, b in enumerate(data)])

# ---------------- DB HELPER ----------------
def register_user_db(username: str, password: str, nik: str):
    conn = connect_db()
    if not conn:
        return False, "Gagal koneksi DB."
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=%s", (username,))
    if cur.fetchone():
        conn.close()
        return False, "Username sudah ada."
    pw_hash = hash_password(password)
    aes_key = get_random_bytes(16)
    encrypted_nik = aes_encrypt_nik(nik, aes_key)
    cur.execute(
        "INSERT INTO users (username, password_hash, nik_encrypted, aes_key) VALUES (%s,%s,%s,%s)",
        (username, pw_hash, encrypted_nik, aes_key.hex())
    )
    conn.commit()
    conn.close()
    return True, "Registrasi berhasil."

def login_user_db(username: str, password: str):
    conn = connect_db()
    if not conn:
        return False, "Gagal koneksi DB."
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, nik_encrypted, aes_key FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "Username tidak ditemukan."
    uid, pw_hash, nik_enc, aes_key_hex = row
    if pw_hash != hash_password(password):
        return False, "Password salah."
    try:
        key_bytes = bytes.fromhex(aes_key_hex)
        nik = aes_decrypt_nik(nik_enc, key_bytes)
    except Exception as e:
        return False, f"Gagal dekripsi NIK: {e}"
    return True, {"user_id": uid, "nik": nik}

def save_file_record(user_id: int, original_name: str, encrypted_b64: str, algorithm: str):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO data_encrypted (user_id, data_type, original_name, encrypted_data, algorithm)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, "file", original_name, encrypted_b64, algorithm))
    conn.commit()
    conn.close()
    return True

# ---------------- UI: STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 Login Sistem Kriptografi")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        ok, res = login_user_db(username, password)
        if ok:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_id = res["user_id"]
            st.session_state.nik = res["nik"]
            st.session_state.page = "main"
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error(res)

    st.write("---")
    st.caption("Belum punya akun?")
    if st.button("Daftar"):
        st.session_state.page = "register"
        st.rerun()

# ---------------- REGISTER PAGE ----------------
def register_page():
    st.title("📝 Register Pengguna Baru")
    username = st.text_input("Username baru")
    password = st.text_input("Password", type="password")
    nik = st.text_input("Masukkan NIK")
    if st.button("Daftar"):
        if not (username and password and nik):
            st.warning("Isi semua kolom.")
        else:
            ok, msg = register_user_db(username, password, nik)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
    st.write("---")
    if st.button("Kembali ke Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- MAIN DASHBOARD ----------------
def main_page():
    st.title("📁 Enkripsi & Dekripsi File (XOR)")
    st.write(f"Login sebagai: **{st.session_state.username}** | NIK: `{st.session_state.nik}`")

    uploaded = st.file_uploader("Pilih file .txt", type=["txt"])
    key = st.text_input("Masukkan kunci XOR (teks)")

    if st.button("🔒 Enkripsi File"):
        if not uploaded or not key:
            st.warning("Pilih file dan isi kunci.")
        else:
            data = uploaded.read()
            result = xor_bytes(data, key)
            b64 = base64.b64encode(result).decode()
            saved = save_file_record(st.session_state.user_id, uploaded.name, b64, "xor")
            if saved:
                st.success("File terenkripsi dan disimpan ke database.")
                st.download_button("Download Encrypted File", data=result, file_name=f"enc_{uploaded.name}")
            else:
                st.error("Gagal menyimpan data.")

    if st.button("🔓 Dekripsi File"):
        if not uploaded or not key:
            st.warning("Pilih file dan isi kunci.")
        else:
            data = uploaded.read()
            try:
                result = xor_bytes(data, key)
                st.success("File berhasil didekripsi.")
                st.download_button("Download Decrypted File", data=result, file_name=f"dec_{uploaded.name}")
            except Exception as e:
                st.error(f"Gagal dekripsi: {e}")

    st.write("---")
    if st.button("🚪 Logout"):
        for k in ["logged_in", "username", "user_id", "nik", "page"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.page = "login"
        st.success("Berhasil logout.")
        st.rerun()

# ---------------- ROUTING ----------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "main":
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()
    else:
        main_page()
