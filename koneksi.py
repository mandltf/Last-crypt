import streamlit as st
import hashlib
import base64
import mysql.connector
from mysql.connector import Error
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# -------------------- Database Config --------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "kriptografi"

# -------------------- Fungsi DB --------------------
def connect_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        return conn
    except Error as e:
        st.error(f"DB connection error: {e}")
        return None