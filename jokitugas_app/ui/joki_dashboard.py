import streamlit as st
import pandas as pd
import os

from database.db import DatabaseManager
from modules.offer import Offer
from modules.progress import ProgressManager
from modules.stats import StatsManager
from modules.auth import AuthManager
from modules.bookmark import Bookmark
from ui.components import UIComponent
from modules.fileutils import FileManager

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "hasil"), exist_ok=True)

class JokiDashboard:
    def __init__(self, username):
        self.username = username
        self.joki_id = AuthManager.get_user_id_by_username(username)
        if self.joki_id is None:
            st.error("Gagal mendapatkan ID Joki.")
            st.stop()

    @staticmethod
    def list_uploaded_versions(task_id):
        folder = os.path.join(UPLOAD_FOLDER, "hasil")
        versions = [
            f for f in os.listdir(folder)
            if f.startswith(f"hasil_{task_id}_v") and f.endswith(".pdf")
        ]
        versions.sort()
        return versions

    @staticmethod
    def save_uploaded_file(uploaded_file, task_id, version_num, file_extension):
        hasil_folder = os.path.join(UPLOAD_FOLDER, "hasil")
        filename = f"hasil_{task_id}_v{version_num}{file_extension}"
        filepath = os.path.join(hasil_folder, filename)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filepath

    @staticmethod
    def get_open_tasks_filtered(keyword="", min_budget=0, max_budget=10_000_000, sort_deadline=False):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        query = "SELECT id, judul, deskripsi, deadline, budget, COALESCE(file_path, '') FROM tasks WHERE status = 'open'"
        params = []

        if keyword:
            query += " AND judul LIKE ?"
            params.append(f"%{keyword}%")

        query += " AND budget BETWEEN ? AND ?"
        params.extend([min_budget, max_budget])

        if sort_deadline:
            query += " ORDER BY deadline ASC"

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return pd.DataFrame(rows, columns=["ID", "Judul", "Deskripsi", "Deadline", "Budget", "FilePath"])

    @staticmethod
    def get_tasks_by_status(joki_username, status, offer_status=None):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        if status in ['in_progress', 'revisi', 'submitted', 'completed']:
            cursor.execute(f"""
                SELECT t.id, t.judul, t.deskripsi, t.deadline, t.budget, t.file_path, t.hasil_file_path
                FROM tasks t
                JOIN offers o ON t.id = o.task_id
                JOIN users u ON o.joki_id = u.id
                WHERE t.status = ? AND u.username = ? AND o.status = 'accepted'
            """, (status, joki_username))
            cols = ["ID", "Judul", "Deskripsi", "Deadline", "Budget", "FilePath", "HasilPath"]
        elif status == 'has_offer':
            cursor.execute(f"""
                SELECT t.id, t.judul, t.deskripsi, t.deadline, t.budget, t.file_path
                FROM tasks t
                JOIN offers o ON t.id = o.task_id
                JOIN users u ON o.joki_id = u.id
                WHERE t.status = ? AND u.username = ? AND o.status = 'pending'
            """, (status, joki_username))
            cols = ["ID", "Judul", "Deskripsi", "Deadline", "Budget", "FilePath"]
        rows = cursor.fetchall()  # <-- Ambil data sebelum close
        conn.close()
        return pd.DataFrame(rows, columns=cols)

    def display_stats(self):
        st.subheader("📊 Statistik Anda")
        stats = StatsManager.get_stats_by_role(self.username, 'joki')
        col1, col2, col3 = st.columns(3)
        col1.metric("Penawaran Dikirim", stats["total_offers"])
        col2.metric("Tugas Diambil", stats["in_progress"])
        col3.metric("Tugas Selesai", stats["completed"])
        st.metric("⭐ Rata-rata Rating", stats["avg_rating"])
        st.markdown("---")

    def display_open_tasks(self):
        st.subheader("🔍 Filter & Daftar Tugas Tersedia")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            keyword = st.text_input("🔎 Judul tugas", key="open_task_keyword")
        with col2:
            min_budget = st.number_input("💰 Min Budget", min_value=0, value=0, step=1000, key="open_task_min_budget")
        with col3:
            max_budget = st.number_input("💰 Max Budget", min_value=0, value=10_000_000, step=1000, key="open_task_max_budget")
        sort_deadline = st.checkbox("⏰ Urutkan berdasarkan deadline", key="open_task_sort_deadline")

        df = JokiDashboard.get_open_tasks_filtered(keyword, min_budget, max_budget, sort_deadline)

        if df.empty:
            st.info("Tidak ada tugas yang cocok dengan filter.")
        else:
            for _, row in df.iterrows():
                with st.expander(f"📌 {row['Judul']} (ID: {row['ID']})"):
                    st.markdown(f"🗓️ Deadline: `{row['Deadline']}` | 💰 Budget: Rp {row['Budget']:,}")
                    st.write(row['Deskripsi'])
                    if row['FilePath']:
                        UIComponent.file_download_button("📥 Download File Tugas", row['FilePath'])
                    else:
                        st.info("Tidak ada file tugas yang diunggah klien.")

                    if Offer.has_submitted_offer(row['ID'], self.username):
                        st.info("✅ Kamu sudah mengirim penawaran ke tugas ini.")
                    else:
                        with st.form(f"offer_form_{row['ID']}"):
                            harga = st.number_input("Harga Penawaran (Rp)", min_value=0, key=f"harga_{row['ID']}")
                            pesan = st.text_area("Pesan untuk Klien", key=f"pesan_{row['ID']}")
                            submit = st.form_submit_button("Kirim Penawaran")

                            if submit:
                                if harga <= 0:
                                    st.warning("Harga tidak boleh nol atau negatif.")
                                elif not pesan.strip():
                                    st.warning("Pesan tidak boleh kosong.")
                                else:
                                    success, msg = Offer.submit_offer(row['ID'], self.username, harga, pesan)
                                    if success:
                                        st.toast("✅ Penawaran berhasil dikirim.")
                                        st.rerun()
                                    else:
                                        st.warning(msg)

                    with st.form(f"bookmark_form_{row['ID']}"):
                        if st.form_submit_button(f"🔖 Simpan Tugas"):
                            if Bookmark.add_bookmark(self.joki_id, row['ID']):
                                st.toast("✅ Tugas disimpan ke bookmark.")
                            else:
                                st.info("Tugas sudah pernah disimpan.")
        st.markdown("---")

    def display_has_offer_tasks(self):
        st.subheader("🟡 Tugas Sedang Ditawar")
        df_has_offer = JokiDashboard.get_tasks_by_status(self.username, 'has_offer')
        if df_has_offer.empty:
            st.info("Tidak ada tugas yang sedang ditawar.")
        else:
            for _, row in df_has_offer.iterrows():
                with st.expander(f"{row['Judul']} (ID: {row['ID']})"):
                    st.markdown(f"🗓️ Deadline: `{row['Deadline']}` | 💰 Budget: Rp {row['Budget']:,}")
                    st.write(row['Deskripsi'])
                    UIComponent.file_download_button("📥 Download File Tugas", row['FilePath'])
                    st.info("Menunggu keputusan klien atas penawaran Anda.")
        st.markdown("---")

    def display_inprogress_tasks(self):
        st.subheader("🟠 Tugas Sedang Dikerjakan")
        df_inprogress = JokiDashboard.get_tasks_by_status(self.username, 'in_progress')
        if df_inprogress.empty:
            st.info("Tidak ada tugas yang sedang dikerjakan.")
        else:
            for _, row in df_inprogress.iterrows():
                with st.expander(f"🟡 {row['Judul']} (ID: {row['ID']})"):
                    st.markdown(f"🗓️ Deadline: `{row['Deadline']}` | 💰 Budget: Rp {row['Budget']:,}")
                    st.write(row['Deskripsi'])
                    UIComponent.file_download_button("📥 Download File Tugas", row['FilePath'])
                    self._handle_task_submission(row['ID'], row['HasilPath'])
        st.markdown("---")

    def display_revisi_tasks(self):
        st.subheader("🔄 Tugas Revisi")
        df_revisi = JokiDashboard.get_tasks_by_status(self.username, 'revisi')
        if df_revisi.empty:
            st.info("Tidak ada tugas revisi.")
        else:
            for _, row in df_revisi.iterrows():
                with st.expander(f"🔄 {row['Judul']} (ID: {row['ID']})"):
                    st.markdown(f"🗓️ Deadline: `{row['Deadline']}` | 💰 Budget: Rp {row['Budget']:,}")
                    st.write(row['Deskripsi'])
                    UIComponent.file_download_button("📥 Download File Tugas", row['FilePath'])
                    st.warning("Tugas ini sedang dalam tahap revisi. Silakan upload hasil revisi sesuai permintaan klien.")
                    self._handle_task_submission(row['ID'], row['HasilPath'])
        st.markdown("---")

    def display_submitted_tasks(self):
        st.subheader("📤 Tugas Dikirim (Menunggu Review Klien)")
        df_submitted = JokiDashboard.get_tasks_by_status(self.username, 'submitted')
        if df_submitted.empty:
            st.info("Tidak ada tugas yang sedang menunggu review klien.")
        else:
            for _, row in df_submitted.iterrows():
                with st.expander(f"📤 {row['Judul']} (ID: {row['ID']})"):
                    st.markdown(f"🗓️ Deadline: `{row['Deadline']}` | 💰 Budget: Rp {row['Budget']:,}")
                    st.write(row['Deskripsi'])
                    UIComponent.file_download_button("📥 Download File Tugas", row['FilePath'])
                    if row['HasilPath']:
                        UIComponent.file_download_button("📄 File Hasil", row['HasilPath'])
                    st.info("Menunggu konfirmasi/review dari klien.")
        st.markdown("---")

    def display_completed_tasks(self):
        st.subheader("✅ Tugas yang Telah Diselesaikan")
        df_completed = JokiDashboard.get_tasks_by_status(self.username, 'completed')
        if df_completed.empty:
            st.info("Belum ada tugas yang selesai.")
        else:
            for _, row in df_completed.iterrows():
                with st.expander(f"✅ {row['Judul']} (ID: {row['ID']})"):
                    st.markdown(f"🗓️ Deadline: `{row['Deadline']}` | 💰 Budget: Rp {row['Budget']:,}")
                    st.write(row['Deskripsi'])
                    UIComponent.file_download_button("📥 File Tugas (Awal)", row['FilePath'])
                    if row['HasilPath']:
                        UIComponent.file_download_button("📄 File Hasil", row['HasilPath'])
        st.markdown("---")

    def display_bookmarked_tasks(self):
        st.subheader("📚 Tugas yang Disimpan")
        bookmarked = Bookmark.get_bookmarked_tasks(self.joki_id)
        if bookmarked:
            st.dataframe(pd.DataFrame(bookmarked, columns=["ID", "Judul", "Deadline", "Budget"]))
        else:
            st.info("Tidak ada tugas yang disimpan.")
        st.markdown("---")

    def _handle_task_submission(self, task_id, current_hasil_path):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, hasil_file_path FROM tasks WHERE id = ?", (task_id,))
        task_row = cursor.fetchone()
        conn.close()
        status_task = task_row[0] if task_row else None
        db_hasil_file_path = task_row[1] if task_row else None

        hasil_folder = os.path.join(UPLOAD_FOLDER, "hasil")
        versions = FileManager.get_all_versions(task_id)
        if versions:
            st.markdown("#### 📜 Histori File Hasil")
            for fname in versions:
                fpath = os.path.join(hasil_folder, fname)
                if os.path.exists(fpath):
                    with open(fpath, "rb") as f:
                        st.download_button(
                            label=f"⬇️ {fname}",
                            data=f,
                            file_name=fname,
                            mime="application/octet-stream",
                            key=f"hist_{task_id}_{fname}"
                        )
            with st.form(f"delete_last_form_{task_id}"):
                if st.form_submit_button(f"🗑️ Hapus Versi Terakhir ({versions[-1]})"):
                    deleted, _ = FileManager.delete_last_file(task_id)
                    if deleted:
                        st.toast("✅ Versi terakhir berhasil dihapus.")
                        st.rerun()
                    else:
                        st.warning("Gagal menghapus versi terakhir.")

        if ProgressManager.can_upload(task_id):
            st.markdown("#### 📤 Upload File Hasil Baru")
            with st.form(f"upload_form_{task_id}"):
                hasil_file = st.file_uploader(
                    "Upload hasil tugas (.pdf, .doc, .zip)",
                    type=["pdf", "doc", "docx", "zip"],
                    key=f"hasil_upload_{task_id}"
                )
                upload_submit = st.form_submit_button("Upload File")

                if upload_submit and hasil_file:
                    next_version = FileManager.get_next_file_version(task_id)
                    ext = os.path.splitext(hasil_file.name)[1]
                    saved_filepath = JokiDashboard.save_uploaded_file(hasil_file, task_id, next_version, ext)

                    conn = DatabaseManager.create_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE tasks SET hasil_file_path = ?, revisi_count = ? WHERE id = ?",
                        (saved_filepath, next_version, task_id)
                    )
                    conn.commit()
                    conn.close()
                    st.toast(f"📄 File hasil v{next_version} berhasil diupload.")
                    st.rerun()
                elif upload_submit and not hasil_file:
                    st.warning("Silakan pilih file untuk diupload.")
        else:
            st.info("Anda tidak dapat mengunggah file saat ini (mungkin tugas sudah selesai atau dibatalkan).")

        if db_hasil_file_path and status_task in ['in_progress', 'revisi']:
            st.success("📄 Hasil sudah diunggah:")
            UIComponent.file_download_button("📄 Unduh Hasil Terbaru", db_hasil_file_path)
            with st.form(f"submit_task_form_{task_id}"):
                if st.form_submit_button("📤 Kirim Hasil ke Klien"):
                    success, msg = ProgressManager.mark_task_submitted(task_id)
                    if success:
                        st.toast("📤 Hasil berhasil dikirim. Menunggu review dari klien.")
                        st.rerun()
                    else:
                        st.warning(msg)
        elif not db_hasil_file_path and status_task in ['in_progress', 'revisi']:
            st.info("Belum ada file hasil yang diunggah untuk tugas ini.")
        st.markdown("---")

    def run(self):
        st.header("🛠️ Dashboard Joki")
        self.display_stats()
        self.display_open_tasks()
        self.display_has_offer_tasks()
        self.display_inprogress_tasks()
        self.display_revisi_tasks()
        self.display_submitted_tasks()
        self.display_completed_tasks()
        self.display_bookmarked_tasks()

def joki_dashboard(username):
    dashboard = JokiDashboard(username)
    dashboard.run()