# 📦 Aplikasi Simulasi Pemesanan Jasa Joki Tugas

## 🎯 Deskripsi Proyek
Aplikasi ini mensimulasikan marketplace antara **klien (mahasiswa)** dan **joki (freelancer)** untuk pemesanan dan pengerjaan tugas digital (coding, laporan, desain, dll).  
Dibangun menggunakan **Python + Streamlit** dan database **SQLite** untuk tugas besar mata kuliah **Pemrograman Berorientasi Objek (PBO)**.

---

## 📁 Struktur Folder

```
jokitugas_app/
│
├── main.py                  # Titik masuk aplikasi Streamlit
├── migrate.py               # Script migrasi database (opsional)
├── README.md                # Dokumentasi proyek
│
├── database/
│   └── db.py                # Koneksi & inisialisasi database SQLite (DatabaseManager)
│
├── modules/
│   ├── auth.py              # class AuthManager: Login, register, session role
│   ├── task.py              # class Task: Pembuatan & pengelolaan tugas
│   ├── offer.py             # class Offer: Penawaran dari joki
│   ├── progress.py          # class ProgressManager: Update status tugas
│   ├── rating.py            # class Rating: Ulasan tugas
│   ├── bookmark.py          # class Bookmark: Bookmark tugas oleh joki
│   ├── favorite.py          # class Favorite: Favorit joki oleh klien
│   ├── fileutils.py         # class FileManager: Utilitas file hasil tugas
│   └── stats.py             # class StatsManager: Statistik dashboard
│
├── ui/
│   ├── klien_dashboard.py   # class KlienDashboard: Tampilan dashboard klien
│   ├── joki_dashboard.py    # class JokiDashboard: Tampilan dashboard joki
│   └── components.py        # class UIComponent: Komponen UI umum (tabel, tombol, toast, dll)
│
├── data/
│   └── joki_app.db          # Database SQLite lokal
│
└── uploaded_files/
    └── hasil/               # Folder file hasil tugas (versi)
```

---

## 🧱 Fitur Utama

- **Autentikasi & Role**
  - Register/login sebagai `klien` atau `joki`
  - Session state dan dashboard sesuai role

- **Manajemen Tugas (Klien)**
  - Membuat tugas baru (judul, deskripsi, deadline, budget, file)
  - Melihat status tugas, menghapus tugas, permintaan revisi

- **Penawaran (Joki)**
  - Melihat daftar tugas open, filter & sort
  - Mengirim penawaran harga & pesan ke klien
  - Bookmark tugas yang menarik

- **Persetujuan Penawaran (Klien)**
  - Melihat penawaran masuk, menerima/menolak penawaran
  - Memilih joki favorit

- **Progress Tugas**
  - Joki upload file hasil (versi), kirim hasil ke klien
  - Klien download hasil, minta revisi, atau menandai selesai

- **Rating & Ulasan**
  - Klien memberi rating & komentar setelah tugas selesai
  - Joki melihat rata-rata rating di dashboard

- **Statistik & Notifikasi**
  - Statistik tugas/penawaran di dashboard
  - Notifikasi interaksi dengan `st.toast()`

---

## 🌟 Fitur Tambahan

| Fitur                  | Status       | Tujuan                        |
|------------------------|--------------|-------------------------------|
| ✅ `st.toast()`        | Prioritas 1  | Notifikasi interaksi          |
| ✅ Statistik Dashboard | Prioritas 2  | Informasi pengguna & sistem   |
| ✅ Filter Tugas        | Prioritas 3  | Aksesibilitas data            |
| ✅ Tugas Mendesak      | Prioritas 4  | Highlight berdasarkan deadline|
| ✅ Bookmark/Favorit    | Prioritas 5  | Simpan joki/tugas             |
| ✅ Riwayat Aktivitas   | Prioritas 6  | Log aktivitas pengguna        |

---

## 🚀 Cara Menjalankan

1. **Install dependensi**
   ```
   pip install streamlit pandas
   ```

2. **Jalankan aplikasi**
   ```
   streamlit run main.py
   ```

3. **(Opsional) Migrasi database**
   ```
   python migrate.py
   ```

---

## 💡 Desain OOP (Simplified)

```python
class User:
    user_id, username, role  # role: 'klien' / 'joki'

class Task:
    task_id, judul, deskripsi, deadline, budget, klien_id, status, file_path

class Offer:
    offer_id, task_id, joki_id, harga_tawaran, pesan, status

class Rating:
    rating_id, task_id, klien_id, nilai, komentar
```

Semua fitur backend dan utilitas sudah di-refactor ke dalam class sesuai standar OOP.

---

## ✅ Tahapan Pengembangan & Milestone

| Tahap | Fitur                                    | Checkpoint                        |
|-------|------------------------------------------|-----------------------------------|
| 0     | Setup struktur proyek & database         | Struktur rapi & database aktif    |
| 1     | Autentikasi + role session               | Bisa login & masuk ke dashboard   |
| 2     | Tugas: Buat & tampilkan (Klien)          | Klien bisa mengelola tugas        |
| 3     | Penawaran (Joki)                         | Joki bisa kirim penawaran         |
| 4     | Persetujuan & status in_progress         | Klien menyetujui penawaran        |
| 5     | Progress & rating                        | Tugas bisa selesai & diberi rating|
| 6.x   | Fitur tambahan (toast, statistik, dll)   | UX meningkat, sistem terasa nyata |

---

## 🙏 Kontribusi & Lisensi

Proyek ini dibuat untuk pembelajaran.  
Silakan gunakan, modifikasi, dan kembangkan sesuai