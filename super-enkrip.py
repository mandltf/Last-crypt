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
    # Langkah 1: Caesar
    hasil_caesar = caesar_encrypt(pesan, shift)
    # Langkah 2: Salsa20
    hasil_salsa = salsa20_encrypt(hasil_caesar, key)
    return hasil_salsa

def super_decrypt(ciphertext, shift, key):
    # Langkah 1: Dekripsi Salsa20
    hasil_salsa = salsa20_decrypt(ciphertext, key)
    # Langkah 2: Dekripsi Caesar
    hasil_caesar = caesar_decrypt(hasil_salsa, shift)
    return hasil_caesar

# ===== Main Program =====
if __name__ == "__main__":
    print("=== Super Enkripsi Caesar_Salsa20 ===")
    print("1. Enkripsi")
    print("2. Dekripsi")
    pilihan = input("Pilih menu (1/2): ")

    shift = int(input("Masukkan kunci Caesar (angka): "))
    key = input("Masukkan kunci Salsa20 (16 karakter): ").encode('utf-8')

    if pilihan == "1":
        pesan = input("Masukkan teks yang mau dienkripsi: ")
        hasil_enkripsi = super_encrypt(pesan, shift, key)
        print("\nHasil Enkripsi (hex):", hasil_enkripsi.hex())

    elif pilihan == "2":
        cipher_hex = input("Masukkan ciphertext (hex): ")
        try:
            ciphertext = bytes.fromhex(cipher_hex)
            hasil_dekripsi = super_decrypt(ciphertext, shift, key)
            print("\nHasil Dekripsi:", hasil_dekripsi)
        except Exception as e:
            print("\n[Error] Gagal dekripsi:", e)
    else:
        print("Pilihan tidak valid.")