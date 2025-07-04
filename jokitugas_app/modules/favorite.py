from database.db import DatabaseManager

class Favorite:
    @staticmethod
    def add_favorite(klien_id, joki_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO favorites (klien_id, joki_id) VALUES (?, ?)", (klien_id, joki_id))
            conn.commit()
            return True
        except:
            return False  # Sudah difavoritkan
        finally:
            conn.close()

    @staticmethod
    def get_favorite_jokis(klien_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username FROM favorites f
            JOIN users u ON f.joki_id = u.id
            WHERE f.klien_id = ?
        """, (klien_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows