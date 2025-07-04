import os
import streamlit as st

class UIComponent:
    UPLOAD_FOLDER = "uploaded_files"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    @staticmethod
    def status_badge(status: str):
        color_map = {
            "draft": "#6c757d",
            "open": "#0d6efd",
            "has_offer": "#ffc107",
            "in_progress": "#fd7e14",
            "submitted": "#20c997",
            "revisi": "#dc3545",
            "completed": "#198754",
        }
        color = color_map.get(status, "#6c757d")
        html = f"""
        <span style='
            background-color: {color};
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        '>{status}</span>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def save_uploaded_file(uploaded_file, username, prefix="tugas"):
        filename = f"{prefix}_{username}_{uploaded_file.name}".replace(" ", "_")
        file_path = os.path.join(UIComponent.UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path

    @staticmethod
    def file_download_button(label: str, file_path: str):
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            st.download_button(
                label=label,
                data=file_bytes,
                file_name=os.path.basename(file_path),
                mime="application/octet-stream"
            )
        else:
            st.info("📁 File tidak ditemukan atau belum tersedia.")

    @staticmethod
    def delete_uploaded_file(file_path: str):
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    @staticmethod
    def get_status_badge(status: str):
        color_map = {
            "open": "#adb5bd",
            "has_offer": "#74c0fc",
            "in_progress": "#fd7e14",
            "submitted": "#51cf66",
            "revisi": "#f783ac",
            "completed": "#087f5b",
        }
        color = color_map.get(status, "#adb5bd")
        html = f"""
        <span style='
            background-color: {color};
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        '>{status}</span>
        """
        st.markdown(html, unsafe_allow_html=True)

    @staticmethod
    def show_uploaded_file_versions(file_list: list):
        if not file_list:
            st.info("Belum ada file hasil yang diupload.")
            return
        st.markdown("#### 📜 Histori File Hasil")
        for fpath in sorted(file_list):
            fname = os.path.basename(fpath)
            if os.path.exists(fpath):
                with open(fpath, "rb") as f:
                    st.download_button(
                        label=f"⬇️ {fname}",
                        data=f,
                        file_name=fname,
                        mime="application/octet-stream",
                        key=f"ver_{fname}"
                    )
            else:
                st.warning(f"File {fname} tidak ditemukan.")

    @staticmethod
    def file_upload_section(task_id, status, revisi_count):
        if status not in ['in_progress', 'revisi']:
            return None

        hasil_folder = os.path.join(UIComponent.UPLOAD_FOLDER, "hasil")
        os.makedirs(hasil_folder, exist_ok=True)
        st.markdown("#### 📤 Upload File Hasil Baru")
        hasil_file = st.file_uploader(
            "Upload hasil tugas (.pdf, .doc, .zip)",
            type=["pdf", "doc", "docx", "zip"],
            key=f"hasil_upload_{task_id}"
        )
        if hasil_file:
            versi = revisi_count + 1 if revisi_count else 1
            ext = os.path.splitext(hasil_file.name)[1]
            hasil_filename = f"hasil_{task_id}_v{versi}{ext}"
            hasil_filepath = os.path.join(hasil_folder, hasil_filename)
            with open(hasil_filepath, "wb") as f:
                f.write(hasil_file.getbuffer())
            st.success(f"File hasil v{versi} berhasil diupload.")
            return hasil_filepath
        return None

    @staticmethod
    def show_revisi_form(task_id: int):
        with st.form(f"revisi_form_{task_id}"):
            alasan = st.text_area("Alasan Permintaan Revisi", key=f"alasan_{task_id}")
            submit = st.form_submit_button("Kirim Permintaan Revisi")
            if submit:
                if not alasan.strip():
                    st.warning("Alasan revisi tidak boleh kosong.")
                    return None
                return alasan