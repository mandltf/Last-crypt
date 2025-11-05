from Crypto.Cipher import Salsa20

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