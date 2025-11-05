# 🔐 Sistem Keamanan Data Kependudukan  
**Implementasi Kriptografi Modern dan Steganografi (LSB) pada Aplikasi Berbasis Streamlit**

## 👩‍💻 Kontributor
- Shafa Kamila Hidayah (123230130)
- Amanda Latifa (123230138)

## 🧩 Deskripsi Singkat
Aplikasi ini merupakan prototipe sistem keamanan data kependudukan yang menggabungkan beberapa teknik kriptografi untuk melindungi informasi sensitif seperti **NIK, alamat, dan dokumen pribadi**.  
Teknologi yang digunakan mencakup:
- **Hashing (SHA-256)** untuk keamanan login.  
- **Enkripsi kombinasi Caesar Cipher + Salsa20** untuk data pribadi.  
- **XOR Cipher** untuk enkripsi file.  
- **Steganografi (LSB)** untuk penyembunyian pesan rahasia di dalam gambar.  

Seluruh data pengguna disimpan di **MySQL Database** dengan kontrol akses melalui fitur login.

---

## 🧠 Alur Sistem
1. **Login & Registrasi**
   - Pengguna mendaftar menggunakan NIK, username, dan password.
   - Password di-*hash* menggunakan SHA-256 sebelum disimpan ke database.
   - Setelah login berhasil, sistem menyimpan `user_id` ke `session_state`.

2. **Dashboard**
   - Setelah login, pengguna diarahkan ke halaman utama (dashboard).
   - Dashboard terdiri dari 3 tab utama:
     - 🧾 **Super Enkripsi Data Pribadi**  
       Menggunakan Caesar Cipher + Salsa20 untuk mengenkripsi data seperti NIK dan alamat.
     - 📂 **Enkripsi File (XOR Cipher)**  
       File dienkripsi byte-per-byte menggunakan kunci rahasia yang dimasukkan pengguna.
     - 🖼️ **Steganografi Gambar (LSB)**  
       Menyembunyikan NIK hasil dekripsi terakhir ke dalam gambar menggunakan algoritma LSB.

3. **Database**
   - Data terenkripsi disimpan di tabel yang berbeda:
     - `users` — Data akun (username, password hash, NIK)
     - `data_pribadi_enkripsi` — Hasil enkripsi NIK, alamat, key Salsa20, dan shift Caesar
     - `data_encrypted` — Hasil enkripsi file
     - `data_stegano` — Hasil steganografi (gambar + pesan tersembunyi)

4. **Dekripsi & Validasi**
   - Sistem dapat mendekripsi kembali data dengan kunci yang sesuai.
   - Pesan hasil ekstraksi dari gambar divalidasi agar cocok dengan NIK pengguna.

---

## 🧱 Struktur Folder
```text
Last-crypt/
│
├── app.py              # File utama (routing login/dashboard)
├── koneksi.py          # Koneksi ke database MySQL
├── login.py            # Halaman login & registrasi
├── super_enkrip.py     # Implementasi Caesar Cipher + Salsa20
├── superteks.py        # Form enkripsi & simpan data pribadi
├── enkrip_file.py      # Enkripsi file dengan XOR
├── stegano.py          # Steganografi gambar (LSB)
└── README.md           # Dokumentasi proyek
```

## ⚙️ Instalasi
Jalankan perintah berikut:
```bash
pip install streamlit pillow pycryptodome mysql-connector-python
```

## 🚀 Cara Menjalankan Aplikasi
Jalankan perintah berikut:
```bash
streamlit run app.py
```
