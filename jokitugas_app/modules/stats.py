from database.db import DatabaseManager
from modules.auth import AuthManager

class StatsManager:
    @staticmethod
    def get_stats_by_role(username, role):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()

        if role == 'klien':
            user_id = AuthManager.get_user_id_by_username(username)

            cursor.execute("SELECT COUNT(*) FROM tasks WHERE klien_id = ?", (user_id,))
            total_tasks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tasks WHERE klien_id = ? AND status = 'completed'", (user_id,))
            completed = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tasks WHERE klien_id = ? AND status = 'in_progress'", (user_id,))
            in_progress = cursor.fetchone()[0]

            conn.close()
            return {
                "total_tasks": total_tasks,
                "completed": completed,
                "in_progress": in_progress
            }

        elif role == 'joki':
            user_id = AuthManager.get_user_id_by_username(username)

            cursor.execute("SELECT COUNT(*) FROM offers WHERE joki_id = ?", (user_id,))
            total_offers = cursor.fetchone()[0]

            # Hitung jumlah tugas yang sedang dikerjakan
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE id IN (
                    SELECT task_id FROM offers 
                    WHERE joki_id = ? AND status = 'accepted'
                ) AND status = 'in_progress'
            """, (user_id,))
            in_progress = cursor.fetchone()[0]

            # Hitung jumlah tugas yang sudah selesai
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE id IN (
                    SELECT task_id FROM offers 
                    WHERE joki_id = ? AND status = 'accepted'
                ) AND status = 'completed'
            """, (user_id,))
            completed = cursor.fetchone()[0]

            # Hitung rata-rata rating dari kolom "nilai"
            cursor.execute("""
                SELECT ROUND(AVG(r.nilai), 2)
                FROM ratings r
                JOIN tasks t ON r.task_id = t.id
                JOIN offers o ON t.id = o.task_id
                WHERE o.joki_id = ? AND o.status = 'accepted'
            """, (user_id,))
            avg_rating = cursor.fetchone()[0] or 0

            conn.close()
            return {
                "total_offers": total_offers,
                "in_progress": in_progress,
                "completed": completed,
                "avg_rating": avg_rating
            }

        conn.close()
        return {}

# Untuk kompatibilitas dengan kode lama
def get_stats_by_role(username, role):
    return StatsManager.get_stats_by_role(username, role)