# main.py
import streamlit as st
from database.db import DatabaseManager
from modules.auth import AuthManager
from modules.progress import ProgressManager

# Inisialisasi tabel saat aplikasi dijalankan pertama kali
DatabaseManager.create_tables()

# Setup awal Streamlit
st.set_page_config(page_title="Aplikasi Joki Tugas", layout="centered")

# Cek session login
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    st.session_state.role = None
    st.session_state.username = None

st.title("📚 Simulasi Pemesanan Jasa Joki Tugas")

# Jika sudah login, tampilkan dashboard sesuai role
if st.session_state.is_logged_in:
    st.success(f"Selamat datang, {st.session_state.username} ({st.session_state.role})!")
    
    # Tombol logout
    if st.button("🔒 Logout"):
        st.session_state.is_logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()
    
    # Tampilkan dashboard sesuai role
    if st.session_state.role == "klien":
        from ui.klien_dashboard import klien_dashboard
        klien_dashboard(st.session_state.username)
    elif st.session_state.role == "joki":
        from ui.joki_dashboard import joki_dashboard
        joki_dashboard(st.session_state.username)

    # --- Validasi status tugas global untuk aksi file (jika ada aksi upload/download di main.py) ---
    # Contoh penggunaan:
    # if st.session_state.get("selected_task_id"):
    #     task_id = st.session_state["selected_task_id"]
    #     if not can_upload(task_id):
    #         st.warning("Anda tidak dapat mengupload file pada status tugas saat ini.")
    #     if not can_download(task_id):
    #         st.warning("File hasil hanya bisa diunduh jika tugas sudah dikirim, revisi, atau selesai.")

else:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Register"])

    # Tampilan login dan register
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login Sekarang"):
            success, username, role = AuthManager.login_user(login_username, login_password)
            if success:
                st.session_state.is_logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.success("Login berhasil! 🔓")
                st.rerun()
            else:
                st.error("Login gagal. Username atau password salah.")

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Buat Username", key="reg_user")
        reg_password = st.text_input("Buat Password", type="password", key="reg_pass")
        reg_role = st.selectbox("Daftar sebagai", ["klien", "joki"])
        if st.button("Daftar Sekarang"):
            success, msg = AuthManager.register_user(reg_username, reg_password, reg_role)