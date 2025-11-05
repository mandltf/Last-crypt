import streamlit as st
import super_enkrip as se
from mysql.connector import Error
from koneksi import connect_db

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
            enc_nik = se.super_encrypt(nik, shift, key)
            enc_alamat = se.super_encrypt(alamat, shift, key)

            # Convert to hex for display and storage
            enc_nik_hex = enc_nik.hex()
            enc_alamat_hex = enc_alamat.hex()
            key_hex = key.hex() 

            # Decrypt for verification
            dec_nik = se.super_decrypt(enc_nik, shift, key)
            dec_alamat = se.super_decrypt(enc_alamat, shift, key)

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