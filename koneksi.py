import streamlit as st
import mysql.connector
from mysql.connector import Error

# konfigurasi database
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "kriptografi"

def connect_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        return conn
    except Error as e:
        st.error(f"DB connection error: {e}")
        return None