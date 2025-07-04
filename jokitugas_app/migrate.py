import sqlite3
from database.db import create_connection

def add_column_if_not_exists(cursor, table, column_name, column_type):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}")
        print(f"✅ Kolom '{column_name}' berhasil ditambahkan ke tabel {table}.")
    else:
        print(f"ℹ️ Kolom '{column_name}' sudah ada di tabel {table}.")

def migrate():
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Tambah kolom status jika belum ada
        add_column_if_not_exists(cursor, "tasks", "status", "TEXT DEFAULT 'draft'")

        # Tambah kolom hasil_path untuk menyimpan path hasil file terakhir
        add_column_if_not_exists(cursor, "tasks", "hasil_path", "TEXT")

        # Tambah kolom revisi_note
        add_column_if_not_exists(cursor, "tasks", "revisi_note", "TEXT")

        # Tambah kolom created_at
        add_column_if_not_exists(cursor, "tasks", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")

        conn.commit()
        print("✅ Migrasi selesai.")
    except Exception as e:
        print("❌ Gagal melakukan migrasi:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()