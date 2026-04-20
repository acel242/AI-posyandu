# 🤖 Test Flow — AI Agent Bot (Aidi) via Telegram

Bot: **Aidi** — Asisten Kesehatan Anak AI di Telegram

---

## 1. Bot Commands

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 1.1 | Kirim `/start` | Pesan selamat datang muncul, penjelasan apa yang bisa Aidi lakukan | ⬜ |
| 1.2 | Kirim `/bantuan` | Daftar perintah & contoh pertanyaan muncul | ⬜ |
| 1.3 | Kirim `/stats` | Statistik Posyandu (total anak, normal, berisiko, alert) | ⬜ |
| 1.4 | Kirim `/batal` | Konfirmasi pembatalan (jika ada proses yang sedang berjalan) | ⬜ |

---

## 2. Chat Bebas — Tanya Jawab AI

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 2.1 | Kirim "halo" | Aidi menyapa dengan ramah | ⬜ |
| 2.2 | Kirim "siapa kamu?" | Aidi menjelaskan dirinya sebagai asisten kesehatan anak | ⬜ |
| 2.3 | Kirim "apa yang bisa kamu lakukan?" | Aidi menjelaskan kemampuannya (cek anak, klasifikasi, jadwal, dll) | ⬜ |
| 2.4 | Kirim pertanyaan kesehatan umum "bagaimana cara mencegah stunting?" | Aidi memberikan informasi yang berguna | ⬜ |
| 2.5 | Kirim pesan kosong atau random "asdfg" | Aidi merespons dengan baik atau minta klarifikasi | ⬜ |

---

## 3. Cek Data Anak

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 3.1 | Kirim "lihat semua anak" / "data anak" | Daftar semua anak terdaftar ditampilkan | ⬜ |
| 3.2 | Kirim "detail anak [nama]" | Detail satu anak (nama, tanggal lahir, status gizi terakhir) | ⬜ |
| 3.3 | Kirim NIK anak yang valid | Detail anak berdasarkan NIK | ⬜ |
| 3.4 | Kirim NIK/Nama yang tidak ada | Aidi bilang tidak ditemukan | ⬜ |
| 3.5 | Kirim "berapa anak yang terdaftar?" | Jumlah total anak | ⬜ |

---

## 4. Klasifikasi Gizi (AI Agent Tool)

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 4.1 | Kirim "klasifikasi gizi anak laki-laki umur 24 bulan berat 10kg tinggi 80cm" | Aidi klasifikasi berdasarkan WHO, sebutkan status (Normal/Stunting/Gizi Buruk/dll) | ⬜ |
| 4.2 | Kirim data dengan angka tidak wajar (berat 50kg untuk bayi) | Aidi memberikan peringatan atau klarifikasi | ⬜ |
| 4.3 | Kirim data tanpa lengkap "anak umur 12 bulan berat 8kg" | Aidi minta data tambahan (tinggi, jenis kelamin) | ⬜ |
| 4.4 | Kirim "apakah anak 6 bulan berat 5.5kg tinggi 65cm normal?" | Aidi jawab berdasarkan standar WHO + Z-score | ⬜ |

---

## 5. Grafik Pertumbuhan

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 5.1 | Kirim "tampilkan grafik [nama anak]" | Aidi kirim gambar grafik pertumbuhan (PNG) | ⬜ |
| 5.2 | Lihat grafik yang dikirim | Ada garis WHO reference + titik data anak, jelas terbaca | ⬜ |
| 5.3 | Kirim "grafik pertumbuhan anak dengan NIK xxx" | Grafik terkirim | ⬜ |
| 5.4 | Kirim untuk anak yang belum punya data pengukuran | Aidi bilang belum ada data cukup untuk grafik | ⬜ |

---

## 6. Jadwal Posyandu

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 6.1 | Kirim "buat jadwal posyandu besok" | Aidi buat jadwal baru, konfirmasi tanggal/waktu | ⬜ |
| 6.2 | Kirim "jadwal posyandu tanggal 15 Juni 2026 jam 09:00 untuk warga" | Jadwal dibuat dengan detail yang tepat | ⬜ |
| 6.3 | Kirim "lihat jadwal" / "daftar jadwal" | Daftar semua jadwal yang sudah dibuat | ⬜ |
| 6.4 | Kirim "jadwal minggu depan" | Jadwal yang akan datang ditampilkan | ⬜ |
| 6.5 | Kirim "reminder 3 hari sebelum jadwal" | Konfirmasi reminder di-set | ⬜ |

---

## 7. Statistik

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 7.1 | Kirim "/stats" | Total anak, normal, berisiko, alert terkirim/gagal/pending | ⬜ |
| 7.2 | Kirim "statistik posyandu" (chat bebas) | Aidi tampilkan statistik | ⬜ |
| 7.3 | Kirim "berapa anak berisiko?" | Jumlah anak berisiko spesifik | ⬜ |

---

## 8. Alert & Notifikasi

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 8.1 | Cek apakah bot kirim alert otomatis | Ada pesan alert untuk anak yang berisiko | ⬜ |
| 8.2 | Lihat format alert | Nama anak, status, saran tindakan | ⬜ |
| 8.3 | Balas alert dengan pertanyaan | Aidi merespons konteks alert tersebut | ⬜ |

---

## 9. Edge Cases

| # | Langkah | Expected Result | ✅ |
|---|---------|----------------|---|
| 9.1 | Kirim pesan sangat panjang (>1000 karakter) | Aidi merespons tanpa crash | ⬜ |
| 9.2 | Kirim emoji saja "👶❤️" | Aidi merespons sesuai konteks | ⬜ |
| 9.3 | Kirim dalam bahasa Inggris | Aidi tetap merespons (mungkin dalam bahasa Inggris) | ⬜ |
| 9.4 | Kirim perintah berturut-turut cepat | Semua diproses, tidak ada yang terlewat | ⬜ |
| 9.5 | Kirim di tengah malam | Bot tetap merespons (24/7) | ⬜ |

---

## 10. Kualitas Respons AI

| # | Cek | Expected | ✅ |
|---|-----|----------|---|
| 10.1 | Bahasa natural | Respons terasa seperti manusia, bukan template | ⬜ |
| 10.2 | Kontekstual | Aidi ingat percakapan sebelumnya dalam sesi | ⬜ |
| 10.3 | Akurat | Data Z-score, klasifikasi WHO benar | ⬜ |
| 10.4 | Helpful | Memberikan saran tindakan, bukan hanya data | ⬜ |
| 10.5 | Tidak hallucinate | Tidak mengarang data anak yang tidak ada | ⬜ |
| 10.6 | Cepat | Respons dalam <10 detik | ⬜ |

---

**Cara Test:**
1. Buka Telegram, cari bot Aidi (atau gunakan link yang sudah diberikan)
2. Kirim `/start` untuk mulai
3. Ikuti checklist di atas satu per satu
4. Tandai ✅ jika berhasil, ❌ jika gagal
5. Laporkan yang ❌ untuk diperbaiki

**Tips:**
- Coba variasi bahasa (formal, informal, campuran)
- Coba data yang salah/tidak lengkap untuk test error handling
- Coba kombinasi perintah (misal: "lihat data anak, lalu klasifikasi yang berisiko")
