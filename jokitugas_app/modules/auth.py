# modules/auth.py

from database.db import DatabaseManager

class AuthManager:
    @staticmethod
    def register_user(username, password, role):
        if not username or not password or role not in ["klien", "joki"]:
            return False, "Semua field harus diisi dengan benar."

        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()

        # Cek apakah username sudah digunakan
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username sudah digunakan."

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        conn.close()
        return True, "Registrasi berhasil!"

    @staticmethod
    def login_user(username, password):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT username, role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return True, result[0], result[1]  # username, role
        else:
            return False, None, None

    @staticmethod
    def get_user_id_by_username(username):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None