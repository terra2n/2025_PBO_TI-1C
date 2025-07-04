from database.db import DatabaseManager

class Bookmark:
    @staticmethod
    def add_bookmark(joki_id, task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO bookmarks (joki_id, task_id) VALUES (?, ?)", (joki_id, task_id))
            conn.commit()
            return True
        except:
            return False  # Sudah pernah dibookmark
        finally:
            conn.close()

    @staticmethod
    def get_bookmarked_tasks(joki_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.judul, t.deadline, t.budget 
            FROM bookmarks b
            JOIN tasks t ON b.task_id = t.id
            WHERE b.joki_id = ?
        """, (joki_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows