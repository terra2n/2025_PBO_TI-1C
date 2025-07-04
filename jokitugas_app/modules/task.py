from database.db import DatabaseManager

class Task:
    @staticmethod
    def create_task(judul, deskripsi, deadline, budget, klien_id, file_path=None):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (judul, deskripsi, deadline, budget, klien_id, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (judul, deskripsi, deadline, budget, klien_id, file_path))
        conn.commit()
        conn.close()

    @staticmethod
    def get_task_by_id(task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    @staticmethod
    def update_task_status(task_id, new_status):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_task(task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_tasks_by_klien(klien_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE klien_id = ?", (klien_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_open_tasks():
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = 'open'")
        rows = cursor.fetchall()
        conn.close()
        return rows