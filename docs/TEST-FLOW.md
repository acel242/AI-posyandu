# 🧪 Manual Test Flow — AI Posyandu Dashboard

Gunakan checklist ini untuk test semua fungsi dari sisi user.

---

## 1. Login Flow

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 1.1 | Buka https://ai-posyandu.vercel.app | Halaman login muncul, background hijau gelap gradient, card putih di tengah | ⬜ |
| 1.2 | Lihat logo dan tulisan "AI Posyandu" | Logo lingkaran hijau dengan "AI", judul besar, subtitle "Sistem Cerdas Posyandu" | ⬜ |
| 1.3 | Coba login tanpa isi apa-apa → klik "Masuk" | Error muncul: "Username dan password harus diisi" | ⬜ |
| 1.4 | Isi username "kader", password salah → klik "Masuk" | Error muncul: "Username atau password salah" | ⬜ |
| 1.5 | Klik tombol mata (👁) di field password | Password terlihat (plain text) | ⬜ |
| 1.6 | Klik lagi tombol mata (🙈) | Password tersembunyi lagi | ⬜ |
| 1.7 | Login sebagai **kader** (username: `kader`, password: `kader123`) | Redirect ke halaman Kader Dashboard | ⬜ |
| 1.8 | Logout, lalu login sebagai **bidan** (`bidan/bidan123`) | Redirect ke Bidan Dashboard | ⬜ |
| 1.9 | Logout, lalu login sebagai **kades** (`kades/kades123`) | Redirect ke Kades Dashboard | ⬜ |

---

## 2. Navbar (Semua Role)

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 2.1 | Lihat navbar di atas | Background putih, teks "AI Posyandu" di kiri, username di kanan | ⬜ |
| 2.2 | Klik tombol 🔔 (bell icon) | Halaman Alert muncul (atau navigasi ke alert page) | ⬜ |
| 2.3 | Jika ada badge merah di bell | Angka menunjukkan jumlah alert gagal | ⬜ |
| 2.4 | Hover tombol "Keluar" | Warna berubah ke merah muda | ⬜ |
| 2.5 | Klik "Keluar" | Kembali ke halaman login | ⬜ |

---

## 3. Dashboard — Kader

Login sebagai `kader/kader123`

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 3.1 | Lihat welcome banner | Hijau gradient, teks "Selamat Datang, kader", tanggal hari ini dalam bahasa Indonesia | ⬜ |
| 3.2 | Lihat kartu peringatan (jika ada) | Kuning, icon ⚠️, jumlah anak >30 hari belum diukur | ⬜ |
| 3.3 | Lihat stat cards | 3 kartu: Total Anak, Normal, Berisiko — masing-masing ada angka dan icon | ⬜ |
| 3.4 | Lihat section "Data Anak" | Ada judul, filter chips (Semua/Normal/Berisiko), dan tabel | ⬜ |
| 3.5 | Klik filter "Semua" | Semua anak ditampilkan | ⬜ |
| 3.6 | Klik filter "Normal" | Hanya anak dengan status normal (hijau) | ⬜ |
| 3.7 | Klik filter "Berisiko" | Hanya anak dengan status kuning/merah | ⬜ |
| 3.8 | Lihat tabel data anak | Kolom: No, Nama, Tanggal Lahir, Jenis Kelamin, Nama Orang Tua, Status, Aksi | ⬜ |
| 3.9 | Hover baris tabel | Baris berubah warna (highlight) | ⬜ |
| 3.10 | Lihat badge status | Hijau "Normal", Kuning "Perhatian", Merah "Bahaya", Biru "Belum Diukur" | ⬜ |
| 3.11 | Klik tombol 📊 (chart) pada salah satu anak | Pindah ke halaman Child Detail dengan grafik pertumbuhan | ⬜ |
| 3.12 | Kembali ke dashboard, klik tombol 🗑️ (hapus) pada salah satu anak | Konfirmasi muncul "Yakin hapus data anak ini?" | ⬜ |
| 3.13 | Klik "Cancel" pada konfirmasi | Tidak jadi hapus, data tetap | ⬜ |
| 3.14 | Klik tombol ➕ FAB di kanan bawah | Modal form "Tambah/Edit Data Anak" muncul | ⬜ |

---

## 4. Form Tambah/Edit Anak

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 4.1 | Lihat modal form | Card putih, ada backdrop blur, judul "Tambah Data Anak" (atau "Edit" jika edit) | ⬜ |
| 4.2 | Lihat field "Nama Anak" | Input text dengan placeholder | ⬜ |
| 4.3 | Lihat field "Tanggal Lahir" | Date picker | ⬜ |
| 4.4 | Lihat field "Jenis Kelamin" | Dropdown: Laki-laki / Perempuan | ⬜ |
| 4.5 | Lihat field "Nama Orang Tua" | Input text | ⬜ |
| 4.6 | Lihat field "Nomor HP Orang Tua" | Input text/number | ⬜ |
| 4.7 | Lihat field "Berat Badan (kg)" | Input number | ⬜ |
| 4.8 | Lihat field "Tinggi Badan (cm)" | Input number | ⬜ |
| 4.9 | Isi semua field dengan data valid, klik "Simpan" | Modal tertutup, data baru muncul di tabel | ⬜ |
| 4.10 | Klik tombol ✕ atau di luar modal | Modal tertutup tanpa simpan | ⬜ |
| 4.11 | Edit data anak yang sudah ada (klik baris) | Modal terbuka dengan data terisi, judul "Edit Data Anak" | ⬜ |
| 4.12 | Ubah salah satu field, klik "Simpan" | Data terupdate di tabel | ⬜ |

---

## 5. Dashboard — Bidan

Login sebagai `bidan/bidan123`

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 5.1 | Lihat welcome banner | "Selamat Datang, bidan" | ⬜ |
| 5.2 | Lihat stat cards | Total Anak, Normal, Berisiko | ⬜ |
| 5.3 | Lihat tabel data anak | Sama seperti kader, semua data terlihat | ⬜ |
| 5.4 | Test filter chips | Semua/Normal/Berisiko berfungsi | ⬜ |
| 5.5 | Klik chart pada salah satu anak | Buka halaman Child Detail | ⬜ |
| 5.6 | Klik FAB ➕ | Form tambah anak muncul | ⬜ |
| 5.7 | Tambah anak baru | Berhasil tersimpan | ⬜ |

---

## 6. Dashboard — Kades

Login sebagai `kades/kades123`

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 6.1 | Lihat welcome banner | "Selamat Datang, kades" | ⬜ |
| 6.2 | Lihat stat cards | Semua angka sama dengan data aktual | ⬜ |
| 6.3 | Lihat tabel data anak | Semua data terlihat | ⬜ |
| 6.4 | Test semua filter | Berfungsi normal | ⬜ |
| 6.5 | Test chart button | Buka Child Detail | ⬜ |
| 6.6 | Test tambah/edit/hapus | Berfungsi normal | ⬜ |

---

## 7. Child Detail (Grafik Pertumbuhan)

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 7.1 | Klik 📊 pada salah satu anak | Halaman Child Detail terbuka | ⬜ |
| 7.2 | Lihat info anak di atas | Nama, tanggal lahir, jenis kelamin terlihat | ⬜ |
| 7.3 | Lihat grafik pertumbuhan | Chart dengan garis WHO reference dan titik data anak | ⬜ |
| 7.4 | Toggle "BB/U" dan "TB/U" | Grafik berganti antara Berat Badan vs Tinggi Badan | ⬜ |
| 7.5 | Lihat summary cards | Tanggal pengukuran terakhir, Z-score, status | ⬜ |
| 7.6 | Lihat tabel riwayat | Semua record pengukuran dengan tanggal dan Z-score | ⬜ |
| 7.7 | Klik tombol "Kembali" | Kembali ke dashboard | ⬜ |

---

## 8. Alert Page

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 8.1 | Klik 🔔 di navbar | Halaman Alert muncul | ⬜ |
| 8.2 | Lihat statistik alert | Total, Terkirim, Gagal, Pending | ⬜ |
| 8.3 | Lihat daftar alert | Nama anak, jenis alert, status | ⬜ |

---

## 9. Responsive Design (Mobile)

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 9.1 | Resize browser ke ~375px (mobile) | Layout menyesuaikan, tidak overflow | ⬜ |
| 9.2 | Test login di mobile | Card pas di layar kecil | ⬜ |
| 9.3 | Test dashboard di mobile | Tabel bisa scroll horizontal, stat cards stack vertikal | ⬜ |
| 9.4 | Test form di mobile | Modal pas di layar, input mudah diisi | ⬜ |

---

## 10. Visual Quality Check

| # | Cek | Expected | ✅ |
|---|-----|----------|---|
| 10.1 | Warna konsisten | Hijau gelap (#0D3B20) sebagai primary, putih dominant | ⬜ |
| 10.2 | Font Inter | Semua teks pakai font Inter | ⬜ |
| 10.3 | Shadow subtle | Card shadows tipis, tidak berlebihan | ⬜ |
| 10.4 | Radius konsisten | Card 12px, button 8px, modal 20px | ⬜ |
| 10.5 | Hover states | Semua button/chip punya efek hover | ⬜ |
| 10.6 | Animasi smooth | Modal muncul dengan animasi, FAB hover scale | ⬜ |

---

**Akun Test:**
- Kader: `kader` / `kader123`
- Bidan: `bidan` / `bidan123`
- Kades: `kades` / `kades123`
- Admin: `admin` / `admin123`
