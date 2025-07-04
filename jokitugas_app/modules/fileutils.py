import os
from datetime import datetime

class FileManager:
    UPLOAD_FOLDER = "uploaded_files"
    HASIL_FOLDER = os.path.join(UPLOAD_FOLDER, "hasil")
    os.makedirs(HASIL_FOLDER, exist_ok=True)

    @staticmethod
    def get_all_versions(task_id):
        """
        Mengembalikan list file hasil_<task_id>_vN.pdf yang ada (sorted by versi ASC).
        """
        files = []
        prefix = f"hasil_{task_id}_v"
        for fname in os.listdir(FileManager.HASIL_FOLDER):
            if fname.startswith(prefix) and fname.endswith(".pdf"):
                files.append(fname)
        # Urutkan berdasarkan nomor versi
        files.sort(key=lambda x: int(x.split("_v")[-1].split(".")[0]))
        return files

    @staticmethod
    def get_next_file_version(task_id):
        """
        Menghasilkan nomor versi berikutnya untuk file hasil_<task_id>_vN.pdf.
        Return: N (int)
        """
        versions = FileManager.get_all_versions(task_id)
        if not versions:
            return 1
        last = versions[-1]
        last_ver = int(last.split("_v")[-1].split(".")[0])
        return last_ver + 1

    @staticmethod
    def delete_last_file(task_id):
        """
        Menghapus file hasil_<task_id>_vN.pdf versi terakhir.
        Return: (True, filename) jika berhasil, (False, None) jika tidak ada file.
        """
        versions = FileManager.get_all_versions(task_id)
        if not versions:
            return False, None
        last_file = versions[-1]
        fpath = os.path.join(FileManager.HASIL_FOLDER, last_file)
        if os.path.exists(fpath):
            os.remove(fpath)
            return True, last_file
        return False, None

    @staticmethod
    def log_file_action(task_id, user, action):
        """
        Mencatat log aktivitas upload/hapus file hasil.
        """
        log_folder = os.path.join(FileManager.UPLOAD_FOLDER, "logs")
        os.makedirs(log_folder, exist_ok=True)
        log_file = os.path.join(log_folder, f"filelog_{task_id}.txt")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {user} {action}\n")