from database.db import DatabaseManager

class Rating:
    @staticmethod
    def insert_rating(task_id, rating, komentar):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ratings (task_id, nilai, komentar)
            VALUES (?, ?, ?)
        """, (task_id, rating, komentar))
        conn.commit()
        conn.close()

    @staticmethod
    def get_rating_by_task(task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nilai, komentar FROM ratings WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        return row