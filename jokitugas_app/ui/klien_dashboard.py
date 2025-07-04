import streamlit as st
import pandas as pd
import datetime
import os

from database.db import DatabaseManager
from modules.offer import Offer
from modules.rating import Rating
from modules.stats import StatsManager
from modules.auth import AuthManager
from modules.favorite import Favorite
from ui.components import UIComponent
from modules.progress import ProgressManager

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class KlienDashboard:
    def __init__(self, username):
        self.username = username
        self.klien_id = AuthManager.get_user_id_by_username(username)
        if self.klien_id is None:
            st.error("Gagal mendapatkan ID Klien.")
            st.stop()

    @staticmethod
    def list_uploaded_versions(task_id):
        folder = "uploaded_files"
        versions = [
            f for f in os.listdir(folder)
            if f.startswith(f"hasil_{task_id}_v") and f.endswith(".pdf")
        ]
        versions.sort()
        return versions

    @staticmethod
    def load_klien_tasks(username):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tasks.id, judul, deskripsi, deadline, budget, status, file_path, hasil_file_path, revisi_note
            FROM tasks
            JOIN users ON tasks.klien_id = users.id
            WHERE users.username = ?
        """, (username,))
        rows = cursor.fetchall()
        conn.close()
        return pd.DataFrame(rows, columns=["ID", "Judul", "Deskripsi", "Deadline", "Budget", "Status", "FilePath", "HasilFilePath", "RevisiNote"])

    def display_stats(self):
        st.subheader("📊 Statistik Tugas Anda")
        stats = StatsManager.get_stats_by_role(self.username, "klien")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", stats["total_tasks"])
        col2.metric("Selesai", stats["completed"])
        col3.metric("Berjalan", stats["in_progress"])
        st.markdown("---")

    def _create_new_task_section(self):
        st.header("📝 Buat Tugas Baru")
        with st.form("form_buat_tugas", clear_on_submit=True):
            judul = st.text_input("Judul Tugas")
            deskripsi = st.text_area("Deskripsi")
            deadline = st.date_input("Deadline", value=datetime.date.today())
            budget = st.number_input("Budget (Rp)", min_value=0, step=5000)
            uploaded_file = st.file_uploader("📎 Upload File (opsional)", type=["pdf", "png", "jpg", "jpeg", "docx"])

            submitted = st.form_submit_button("🚀 Submit Tugas")

            if submitted:
                if not judul.strip():
                    st.warning("Judul tidak boleh kosong.")
                    return
                if budget <= 0:
                    st.warning("Budget harus positif.")
                    return
                if deadline < datetime.date.today():
                    st.warning("Deadline tidak boleh di masa lalu.")
                    return

                file_path = None
                if uploaded_file is not None:
                    file_name = f"{self.username}_{judul}_{uploaded_file.name}".replace(" ", "_")
                    file_path = os.path.join(UPLOAD_FOLDER, file_name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                conn = DatabaseManager.create_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks (judul, deskripsi, deadline, budget, klien_id, file_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (judul, deskripsi, deadline.strftime("%Y-%m-%d"), budget, self.klien_id, file_path))
                conn.commit()
                conn.close()

                st.toast("✅ Tugas berhasil ditambahkan!")
                st.success("Tugas berhasil dibuat.")
                st.rerun()
        st.markdown("---")

    def _display_task_card(self, row):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**Deskripsi:** {row['Deskripsi']}")
        col2.markdown("**Status:**")
        UIComponent.get_status_badge(row["Status"])

        st.markdown(f"**Deadline:** {row['Deadline']}  \n**Budget:** Rp {row['Budget']:,}")
        UIComponent.file_download_button("📥 Unduh File Tugas", row["FilePath"])

        if row["Status"] == "revisi" and row["RevisiNote"]:
            st.warning(f"**Catatan Revisi:** {row['RevisiNote']}")

    def _display_result_files(self, row):
        if ProgressManager.can_download(row["ID"]):
            if row["HasilFilePath"] and os.path.exists(row["HasilFilePath"]):
                with open(row["HasilFilePath"], "rb") as f:
                    st.download_button(
                        label="📥 Unduh File Hasil Terbaru",
                        data=f,
                        file_name=os.path.basename(row["HasilFilePath"]),
                        mime="application/octet-stream",
                        key=f"hasil_latest_{row['ID']}"
                    )
            else:
                st.info("Belum ada file hasil yang diunggah.")

            st.markdown("### 📂 Riwayat File Hasil")
            versions = KlienDashboard.list_uploaded_versions(row["ID"])
            if versions:
                for fname in versions:
                    with open(os.path.join("uploaded_files", fname), "rb") as f:
                        st.download_button(f"⬇️ Unduh {fname}", f, file_name=fname, key=f"ver_{row['ID']}_{fname}")
            else:
                st.info("Tidak ada riwayat file hasil.")

    def _section_cari_joki(self, df_tasks):
        st.header("🔎 Sedang Cari Joki")
        if df_tasks.empty:
            st.info("Tidak ada tugas yang sedang mencari joki.")
        else:
            for _, row in df_tasks.iterrows():
                with st.expander(f"📄 {row['Judul']} - ID: {row['ID']}"):
                    self._display_task_card(row)
                    if st.button("🗑️ Hapus Tugas", key=f"hapus_open_{row['ID']}"):
                        conn = DatabaseManager.create_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM tasks WHERE id = ?", (row["ID"],))
                        conn.commit()
                        conn.close()
                        st.toast("🗑️ Tugas berhasil dihapus.")
                        st.rerun()
        st.markdown("---")

    def _section_penawaran_masuk(self, df_tasks):
        st.header("💬 Penawaran Masuk dari Joki")
        if df_tasks.empty:
            st.info("Tidak ada tugas dengan penawaran masuk.")
        else:
            for _, row in df_tasks.iterrows():
                with st.expander(f"📄 {row['Judul']} - ID: {row['ID']}"):
                    self._display_task_card(row)
                    offers = Offer.get_offers_by_task(row["ID"])
                    if offers:
                        st.markdown("### 📨 Detail Penawaran")
                        for offer in offers:
                            joki_username, harga, pesan, status, offer_id = offer
                            with st.container(border=True):
                                st.write(f"🧑 Joki: `{joki_username}` | 💰 Harga: Rp {harga:,}")
                                st.write(f"💬 Pesan: {pesan}")
                                st.write(f"📌 Status: `{status}`")

                                if status == "pending":
                                    with st.form(key=f"offer_action_{offer_id}"):
                                        colA, colB = st.columns(2)
                                        with colA:
                                            if st.form_submit_button("✅ Terima Penawaran"):
                                                Offer.accept_offer(offer_id, row["ID"])
                                                st.toast("✅ Penawaran diterima.")
                                                st.rerun()
                                        with colB:
                                            if st.form_submit_button("❌ Tolak Penawaran"):
                                                Offer.reject_offer(offer_id)
                                                st.toast("❌ Penawaran ditolak.")
                                                st.rerun()

                                joki_id = AuthManager.get_user_id_by_username(joki_username)
                                if st.button(f"❤️ Favoritkan Joki: {joki_username}", key=f"fav_{offer_id}"):
                                    if Favorite.add_favorite(self.klien_id, joki_id):
                                        st.toast("💖 Joki ditambahkan ke favorit!")
                                    else:
                                        st.info("Joki sudah difavoritkan.")
                    else:
                        st.info("📭 Belum ada penawaran untuk tugas ini.")
                    if st.button("🗑️ Hapus Tugas", key=f"hapus_offer_{row['ID']}"):
                        conn = DatabaseManager.create_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM tasks WHERE id = ?", (row["ID"],))
                        conn.commit()
                        conn.close()
                        st.toast("🗑️ Tugas berhasil dihapus.")
                        st.rerun()
        st.markdown("---")

    def _section_sedang_dikerjakan(self, df_tasks):
        st.header("🏗️ Sedang Dikerjakan oleh Joki")
        if df_tasks.empty:
            st.info("Tidak ada tugas yang sedang dikerjakan.")
        else:
            for _, row in df_tasks.iterrows():
                with st.expander(f"📄 {row['Judul']} - ID: {row['ID']}"):
                    self._display_task_card(row)
        st.markdown("---")

    def _section_hasil_dikirim_revisi(self, df_tasks):
        st.header("📥 Hasil Tugas Dikirim / Revisi")
        if df_tasks.empty:
            st.info("Tidak ada tugas dengan hasil dikirim atau dalam revisi.")
        else:
            for _, row in df_tasks.iterrows():
                with st.expander(f"📄 {row['Judul']} - ID: {row['ID']}"):
                    self._display_task_card(row)
                    self._display_result_files(row)

                    if row["Status"] == "submitted" or row["Status"] == "revisi":
                        with st.form(f"action_form_{row['ID']}"):
                            st.markdown("### Tindakan Terhadap Hasil")
                            col_revisi_submit, col_complete = st.columns(2)
                            with col_revisi_submit:
                                alasan = st.text_area("Alasan Permintaan Revisi", key=f"alasan_{row['ID']}")
                                if st.form_submit_button("Kirim Permintaan Revisi"):
                                    if not alasan.strip():
                                        st.warning("Alasan revisi tidak boleh kosong.")
                                    else:
                                        conn = DatabaseManager.create_connection()
                                        cursor = conn.cursor()
                                        cursor.execute(
                                            "UPDATE tasks SET status = 'revisi', revisi_note = ? WHERE id = ?",
                                            (alasan, row["ID"])
                                        )
                                        conn.commit()
                                        conn.close()
                                        st.toast("🔄 Permintaan revisi telah dikirim.")
                                        st.rerun()
                            with col_complete:
                                st.write(" ") # Spacer
                                if st.form_submit_button("✅ Tandai Selesai"):
                                    conn = DatabaseManager.create_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (row["ID"],))
                                    conn.commit()
                                    conn.close()
                                    st.toast("✅ Tugas berhasil diselesaikan.")
                                    st.rerun()
        st.markdown("---")

    def _section_tugas_selesai(self, df_tasks):
        st.header("✅ Tugas Selesai")
        if df_tasks.empty:
            st.info("Tidak ada tugas yang sudah selesai.")
        else:
            for _, row in df_tasks.iterrows():
                with st.expander(f"📄 {row['Judul']} - ID: {row['ID']}"):
                    self._display_task_card(row)
                    self._display_result_files(row)
                    rating_data = Rating.get_rating_by_task(row["ID"])
                    if rating_data:
                        st.success(f"⭐ Rating: {rating_data[0]}  \n💬 Ulasan: {rating_data[1]}")
                    else:
                        with st.form(f"rating_form_{row['ID']}"):
                            st.markdown("### 🌟 Berikan Rating")
                            rating = st.slider("Nilai (1–5)", 1, 5, key=f"rating_slider_{row['ID']}")
                            komentar = st.text_area("Komentar", key=f"komentar_rating_{row['ID']}")
                            if st.form_submit_button("Kirim Rating"):
                                Rating.insert_rating(row["ID"], rating, komentar)
                                st.toast("⭐ Rating berhasil dikirim.")
                                st.rerun()
        st.markdown("---")

    def display_favorite_jokis(self):
        st.subheader("⭐ Joki Favorit Anda")
        favorites = Favorite.get_favorite_jokis(self.klien_id)
        if favorites:
            fav_df = pd.DataFrame(favorites, columns=["ID", "Username"])
            st.table(fav_df)
        else:
            st.info("Tidak ada joki favorit.")
        st.markdown("---")

    def run(self):
        st.title("📋 Dashboard Klien")
        self.display_stats()
        self._create_new_task_section()

        df_all_tasks = KlienDashboard.load_klien_tasks(self.username)

        # Filter tasks by status for each section
        df_open = df_all_tasks[df_all_tasks["Status"] == "open"]
        df_has_offer = df_all_tasks[df_all_tasks["Status"] == "has_offer"]
        df_in_progress = df_all_tasks[df_all_tasks["Status"] == "in_progress"]
        df_submitted_revisi = df_all_tasks[df_all_tasks["Status"].isin(["submitted", "revisi"])]
        df_completed = df_all_tasks[df_all_tasks["Status"] == "completed"]

        self._section_cari_joki(df_open)
        self._section_penawaran_masuk(df_has_offer)
        self._section_sedang_dikerjakan(df_in_progress)
        self._section_hasil_dikirim_revisi(df_submitted_revisi)
        self._section_tugas_selesai(df_completed)
        self.display_favorite_jokis()

def klien_dashboard(username):
    dashboard = KlienDashboard(username)
    dashboard.run()