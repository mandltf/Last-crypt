import streamlit as st
import login
import superteks
import enkrip_file
import stegano

if "page" not in st.session_state:
    st.session_state["page"] = "login"

# Routing
if st.session_state["page"] == "login":
    login.login_page()
elif st.session_state["page"] == "register":
    login.register_page()
elif st.session_state["page"] == "dashboard":
    st.title("Dashboard")

    st.write(f"Selamat datang, **{st.session_state.name}** 👋")

    tab1, tab2, tab3 = st.tabs(["🔐 Input Data Pribadi", "📂 Unggah Berkas", "🖼️ Input Foto Diri/Kartu identitas"])

    with tab1:
        superteks.supertext()

    with tab2:
        enkrip_file.file_encrypt()

    with tab3:
        stegano.stegano()

    st.write("---")
    if st.button("Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()