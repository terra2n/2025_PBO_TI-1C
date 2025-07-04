from database.db import DatabaseManager

class Offer:
    valid_transitions = {
        'draft': ['open'],
        'open': ['has_offer'],
        'has_offer': ['in_progress'],
        'in_progress': ['submitted'],
        'submitted': ['revisi', 'completed'],
        'revisi': ['submitted']
    }

    @staticmethod
    def is_valid_transition(current_status, new_status):
        return new_status in Offer.valid_transitions.get(current_status, [])

    @staticmethod
    def _get_connection():
        return DatabaseManager.create_connection()

    @staticmethod
    def submit_offer(task_id, joki_username, harga, pesan):
        conn = Offer._get_connection()
        cursor = conn.cursor()

        # Ambil ID joki dari username
        cursor.execute("SELECT id FROM users WHERE username = ?", (joki_username,))
        joki = cursor.fetchone()
        if not joki:
            conn.close()
            return False, "User joki tidak ditemukan."

        joki_id = joki[0]

        # Cek apakah sudah pernah mengirim penawaran ke tugas ini
        cursor.execute("SELECT * FROM offers WHERE task_id = ? AND joki_id = ?", (task_id, joki_id))
        if cursor.fetchone():
            conn.close()
            return False, "Anda sudah mengirim penawaran ke tugas ini."

        # Simpan penawaran baru
        cursor.execute("""
            INSERT INTO offers (task_id, joki_id, harga_tawaran, pesan)
            VALUES (?, ?, ?, ?)
        """, (task_id, joki_id, harga, pesan))

        # Update status task jika sebelumnya masih open
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        current_status = cursor.fetchone()[0]
        if current_status == 'open' and Offer.is_valid_transition(current_status, 'has_offer'):
            cursor.execute("UPDATE tasks SET status = 'has_offer' WHERE id = ?", (task_id,))

        conn.commit()
        conn.close()
        return True, "Penawaran berhasil dikirim."

    @staticmethod
    def has_submitted_offer(task_id, joki_username):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ?", (joki_username,))
        joki = cursor.fetchone()
        if not joki:
            conn.close()
            return False

        joki_id = joki[0]
        cursor.execute("SELECT * FROM offers WHERE task_id = ? AND joki_id = ?", (task_id, joki_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def get_offers_by_task(task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.username, o.harga_tawaran, o.pesan, o.status, o.id
            FROM offers o
            JOIN users u ON o.joki_id = u.id
            WHERE o.task_id = ?
        """, (task_id,))
        offers = cursor.fetchall()
        conn.close()
        return offers

    @staticmethod
    def accept_offer(offer_id, task_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()

        # Terima penawaran ini
        cursor.execute("UPDATE offers SET status = 'accepted' WHERE id = ?", (offer_id,))

        # Cek status tugas saat ini
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        current_status = cursor.fetchone()[0]

        # Ubah status tugas ke in_progress jika valid
        if Offer.is_valid_transition(current_status, 'in_progress'):
            cursor.execute("UPDATE tasks SET status = 'in_progress' WHERE id = ?", (task_id,))

        # Tolak penawaran lain
        cursor.execute("UPDATE offers SET status = 'rejected' WHERE task_id = ? AND id != ?", (task_id, offer_id))

        conn.commit()
        conn.close()

    @staticmethod
    def reject_offer(offer_id):
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE offers SET status = 'rejected' WHERE id = ?", (offer_id,))