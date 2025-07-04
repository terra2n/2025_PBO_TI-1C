# database/db.py

import sqlite3
import os

class DatabaseManager:
    DB_PATH = os.path.join("data", "joki_app.db")

    @staticmethod
    def create_connection():
        return sqlite3.connect(DatabaseManager.DB_PATH)

    @staticmethod
    def create_tables():
        conn = DatabaseManager.create_connection()
        cursor = conn.cursor()

        # === Tabel Pengguna ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('klien', 'joki'))
            )
        """)

        # === Tabel Tugas ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                deskripsi TEXT,
                deadline TEXT,
                budget INTEGER,
                status TEXT DEFAULT 'draft',
                klien_id INTEGER,
                file_path TEXT,
                hasil_path TEXT,
                revisi_note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (klien_id) REFERENCES users(id)
            )
        """)

        # === Tabel Penawaran ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                joki_id INTEGER,
                harga_tawaran INTEGER,
                pesan TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (joki_id) REFERENCES users(id)
            )
        """)

        # === Tabel Rating ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                klien_id INTEGER,
                nilai INTEGER,
                komentar TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (klien_id) REFERENCES users(id)
            )
        """)

        # === Tabel Bookmark (tugas yang disimpan joki) ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                joki_id INTEGER,
                task_id INTEGER,
                UNIQUE(joki_id, task_id),
                FOREIGN KEY (joki_id) REFERENCES users(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)

        # === Tabel Favorit (joki favorit klien) ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                klien_id INTEGER,
                joki_id INTEGER,
                UNIQUE(klien_id, joki_id),
                FOREIGN KEY (klien_id) REFERENCES users(id),
                FOREIGN KEY (joki_id) REFERENCES users(id)
            )
        """)

        # === Tabel Histori File Hasil (versi file revisi) ===
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hasil_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                file_path TEXT,
                versi INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)

        conn.commit()
        conn.close()

# Untuk kompatibilitas dengan kode lama
def create_connection():
    return DatabaseManager.create_connection()

def create_tables():
    return DatabaseManager.create_tables()