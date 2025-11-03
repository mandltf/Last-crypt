import streamlit as st
import hashlib
from Crypto.Cipher import AES, Salsa20
import mysql.connector
import base64
from PIL import Image

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",      # default MySQL user
        password="",      # isi password kamu (kalau XAMPP biasanya kosong)
        database="kriptografi"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password, NIK):
    db = connect_db()
    cur = db.cursor()
    hashed_password = hash_password(password)
    cur.execute("INSERT INTO users (username, password, NIK) VALUES (%s, %s, %s)", (username, hashed_password, NIK))
    db.commit()
    db.close()

def login(username, password):
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    data = cur.fetchone()
    db.close()
    if data and data[0] == hash_password(password):
        return True
    return False 

