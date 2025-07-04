# modules/progress.py

import os
from database.db import DatabaseManager

class ProgressManager:
    # 🔁 Validasi transisi status antar tugas
    @staticmethod
    def is_valid_status_transition(current, target):
        valid_transitions = {
            "draft": ["open"],
            "open": ["has_offer"],
            "has_offer": ["in_progress"],
            "in_progress": ["submitted"],
            "submitted": ["revisi", "completed"],
            "revisi": ["submitted"],
            "completed": []
        }
        return target in valid_transitions.get(current, [])

    # ✅ Fungsi umum update status dengan validasi
    @staticmethod
    def update_task_status(task_id, new_status):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "❌ Tugas tidak ditemukan."

        current_status = row[0]
        if not ProgressManager.is_valid_status_transition(current_status, new_status):
            conn.close()
            return False, f"⛔ Transisi status dari '{current_status}' ke '{new_status}' tidak valid."

        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        conn.close()
        return True, f"✅ Status berhasil diubah dari '{current_status}' ke '{new_status}'."

    # 🧾 Fungsi shortcut modular untuk update status
    @staticmethod
    def mark_task_submitted(task_id):
        return ProgressManager.update_task_status(task_id, "submitted")

    @staticmethod
    def mark_task_revision(task_id):
        return ProgressManager.update_task_status(task_id, "revisi")

    @staticmethod
    def mark_task_completed(task_id):
        return ProgressManager.update_task_status(task_id, "completed")

    @staticmethod
    def mark_task_open(task_id):
        return ProgressManager.update_task_status(task_id, "open")

    @staticmethod
    def mark_task_in_progress(task_id):
        return ProgressManager.update_task_status(task_id, "in_progress")

    @staticmethod
    def mark_task_has_offer(task_id):
        return ProgressManager.update_task_status(task_id, "has_offer")

    # === Helper untuk validasi dan hak akses status tugas ===
    @staticmethod
    def get_task_status(task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return None

    @staticmethod
    def can_upload(task_id):
        status = ProgressManager.get_task_status(task_id)
        return status in ["in_progress", "revisi"]

    @staticmethod
    def can_delete(task_id):
        status = ProgressManager.get_task_status(task_id)
        return status in ['in_progress', 'revisi']

    @staticmethod
    def can_download(task_id):
        status = ProgressManager.get_task_status(task_id)
        return status in ['submitted', 'revisi', 'completed']

    @staticmethod
    def is_task_editable(task_id):
        status = ProgressManager.get_task_status(task_id)
        return status != 'completed'

    @staticmethod
    def get_task_owner(task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT klien_id FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return None

    @staticmethod
    def valid_task_transition(current, target):
        return ProgressManager.is_valid_status_transition(current, target)

    @staticmethod
    def get_next_file_version(task_id):
        folder = "uploaded_files"
        existing_files = [
            f for f in os.listdir(folder)
            if f.startswith(f"hasil_{task_id}_v") and f.endswith(".pdf")
        ]

        if not existing_files:
            return 1

        versions = []
        for fname in existing_files:
            try:
                versi = int(fname.split("_v")[-1].replace(".pdf", ""))
                versions.append(versi)
            except:
                pass

        return max(versions) + 1 if versions else 1