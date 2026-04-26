# FORMAT PROPOSAL PROGRAM BCA

---

# COVER

## AI-POSYANDU v2.0
### Platform AI Agent untuk Pencegahan Stunting dan Aktivasi Posyandu

**Program:** Gerakan Berbakti untuk Indonesia Lebih Sehat  
**Lokasi:** Desa Patakbanteng, Wonosobo, Jawa Tengah  
**Tanggal:** April 2026  
**Versi:** 2.0  

---

# HALAMAN IDENTITAS

| Field | Detail |
|-------|--------|
| **Nama Program** | AI-Posyandu Wonosobo v2.0 |
| **Jenis Program** | Teknologi AI untuk Kesehatan Masyarakat |
| **Lokasi Implementasi** | Desa Patakbanteng, Kecamatan Kejajar, Kabupaten Wonosobo, Jawa Tengah |
| **Pelaksanaan Program** | 8 Juli - 6 Agustus 2026 (30 hari) |
| **Durasi Program** | 4 Minggu (Pilot) |
| **Penanggung Jawab** | Tim Pengembangan AI-Posyandu |
| **Kontak** | - |
| **Target Beneficiaries** | 50+ balita dan keluarga di Patakbanteng |
| **Anggaran** | Rp 5.500.000 (Total) |

---

# RINGKASAN

AI-Posyandu adalah platform berbasis AI Agent yang dirancang untuk membantu pencegahan stunting dan aktivasi Posyandu di Desa Patakbanteng, Wonosobo, Jawa Tengah. Sistem ini terdiri dari Telegram Bot untuk interaksi warga, dashboard web untuk Kader/Bidan, dan AI reasoning untuk klasifikasi status gizi balita berdasarkan standar WHO.

**Permasalahan Utama:**
- AI chat masih berbasis keyword matching (LIKE query), bukan semantic search
- Tidak ada sistem RAG (Retrieval Augmented Generation) untuk jawaban berbasis data
- Dashboard belum memiliki visualisasi tren stunting per wilayah
- Belum ada sistem alert otomatis untuk balita dengan Z-score berisiko
- Belum ada integrasi dengan sistem Puskesmas/Faskes lain

**Solusi yang Ditawarkan:**
1. Semantic Search dengan Embeddings — upgrade dari keyword ke semantic search
2. RAG Pipeline — AI chat mengambil konteks dari database
3. Auto-Alert System — notifikasi otomatis untuk balita berisiko
4. Dashboard Tren Stunting — visualisasi Z-score distribution

**Angka Kunci:**
- Total Balita Terdaftar: 50+ (pilot Patakbanteng)
- Estimasi Biaya Bulanan: Rp 250.000 - 650.000
- Target Penurunan Stunting: > 10% per tahun

---

# BAB I ANALISIS MASALAH

## 1.1 Latar Belakang Stunting di Indonesia

Stunting adalah kondisi gagal tumbuh pada balita akibat kekurangan gizi kronis. Prevalensi stunting di Indonesia masih tinggi:

| Wilayah | Prevalensi Stunting |
|--------|-------------------|
| Nasional | 21,6% (SSGI 2023) |
| Jawa Tengah | 20,3% |
| Wonosobo | ~25% (di atas rata-rata nasional) |

## 1.2 Permasalahan di Desa Patakbanteng

**Kondisi Geografis:**
- Desa di ketinggian (~900m dpl), akses ke Puskesmas jauh
- Banyak dusun terpencil dengan internet terbatas

**Kondisi SDM:**
- Kader umumnya ibu-ibu rumah tangga, keterbatasan teknologi
- Bidan hanya 1 untuk beberapa desa

**Kondisi Data:**
- Pencatatan masih manual di buku KIA
- Data tidak terstandarisasi antar Posyandu
- Tidak ada sistem alert untuk balita berisiko

## 1.3 Analisis Permasalahan per Stakeholder

### Dari Sisi Warga

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Tidak tahu jadwal Posyandu | Perlu tanya kader setiap bulan | Tinggi |
| Tidak tahu status gizi anak | Tidak ada cara track mandiri | Tinggi |
| Bingung tanya soal nutrisi | Tidak ada yang bisa ditanya kapan saja | Sedang |
| Tidak ada reminder | Lupa jadwal penimbangan | Tinggi |

### Dari Sisi Kader

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Buku KIA penuh | Catat manual, susah cari data lama | Tinggi |
| Tidak ada alarm untuk anak berisiko | Harus ingat sendiri mana anak bermasalah | Tinggi |
| Workload tinggi | 1 kader handle 30-50 balita | Tinggi |

### Dari Sisi Bidan

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Data dari berbagai Posyandu tidak unify | Harus kumpulkan dari banyak buku | Tinggi |
| Tidak ada sistem alert | Tidak tahu balita baru masuk zona merah | Tinggi |
| Laporan bulanan manual | Hitung manual, prone error | Tinggi |

## 1.4 Capaian Sistem Saat Ini (v1.5)

| Komponen | Status | Keterangan |
|----------|--------|------------|
| Telegram Bot | ✅ Aktif | @bot, registrasi, chat AI, reminder |
| Dashboard Kader | ✅ Aktif | React, statistik anak, input data |
| Dashboard Bidan | ✅ Aktif | Detail anak, rekam medis, klasifikasi |
| Dashboard Kepala Desa | ✅ Aktif | Overview seluruh desa, statistik |
| AI BB/TB Classifier | ✅ Aktif | WHO Z-score: -1 SD (normal), -3 SD to < -1 SD (risiko), < -3 SD (berat) |
| Auto-notification | ✅ Aktif | Reminder jadwal imunisasi via bot |
| Database | ✅ Aktif | SQLite, 100KB+ data anak |

---

# BAB II METODE PELAKSANAAN

## 2.1 Metode Pengumpulan Data

### Data Primer
- **Registrasi Warga:** Via Telegram Bot dengan validasi Kader
- **Pengukuran Anthropometri:** Input manual oleh Kader via dashboard
- **Chat Interaction:** Data percakapan AI untuk improvement

### Data Sekunder
- **Buku KIA** — Data historis balita dari catatan manual
- **Standar WHO** — Tabel Z-score untuk klasifikasi
- **PMBA (Pedoman Makan Bayi dan Balita)** — Kemenkes RI

## 2.2 Metode Analisis

### AI Z-Score Classification
Menggunakan standar WHO Z-score:
- 🟢 Normal: ≥ -1 SD
- 🟡 Risiko: -3 SD ≤ Z < -1 SD
- 🔴 Berat: < -3 SD

### Semantic Search
Upgrade dari keyword LIKE query ke TF-IDF/semantic embeddings untuk pencarian yang lebih akurat.

## 2.3 Timeline Implementasi

| Minggu | Tanggal | Aktivitas | Output |
|--------|---------|-----------|--------|
| 1 | 8-14 Juli 2026 | Setup environment, semantic search + RAG implementation | Dev environment ready, AI chat works |
| 2 | 15-21 Juli 2026 | Knowledge base setup, auto-alert system | PMBA/WHO loaded, auto alerts working |
| 3 | 22-28 Juli 2026 | Dashboard tren stunting, monitoring kinerja Kader | Visualisasi Z-score aktif |
| 4 | 29 Juli - 6 Agustus 2026 | Testing, pilot evaluation, handover | Sistem siap beroperasi, dokumentasi lengkap |

## 2.4 Teknologi yang Digunakan

| Layer | Teknologi |
|-------|-----------|
| Frontend Web | React 18 + Vite + Tailwind |
| Backend API | Flask (Python) port 5001 |
| Bot | Python Telegram Bot + python-dotenv |
| AI Chat | Deepseek v4-pro/v4-flash (OpenAI-compatible) |
| AI Classification | Rule-based WHO Z-score calculator |
| Database | SQLite (posyandu.db) |
| Scheduler | APScheduler (auto-notification) |

---

# BAB III PROGRAM KERJA & RENCANA ANGGARAN

## 3.1 Rencana Pengembangan (v2.0)

### Fase 1 — AI & RAG Upgrade (2-3 minggu)

| Aktivitas | Deskripsi |
|-----------|-----------|
| Semantic Search | Upgrade dari keyword LIKE → semantic search menggunakan embeddings |
| RAG Pipeline | AI chat mengambil konteks dari database sebelum menjawab |
| Knowledge Base | Dokumen PMBA, standar WHO, kebijakan stunting lokal |

### Fase 2 — Alert & Monitoring (2-3 minggu)

| Aktivitas | Deskripsi |
|-----------|-----------|
| Auto-Alert Z-Score | Sistem auto-detect balita dengan Z-score kuning/merah |
| Dashboard Tren Stunting | Visualisasi Z-score distribution per bulan |
| Monitoring Kinerja Kader | Track: berapa banyak balita tiap Kader, compliance rate imunisasi |

### Fase 3 — Integrasi & Skalabilitas (3-4 minggu)

| Aktivitas | Deskripsi |
|-----------|-----------|
| Integrasi Puskesmas/Faskes | API untuk bidirectional data exchange |
| Mobile App | **(SKIP — fokus dashboard web)** |
| Multi-Desa Scaling | Sistem support multiple villages |
| Laporan Otomatis | Generate laporan bulanan untuk Dinas Kesehatan |

## 3.2 Estimasi Biaya Operasional

| Komponen | Biaya/Bulan | Keterangan |
|----------|-------------|------------|
| VPS (server) | Rp 200.000 - 500.000 | Depends on specs needed |
| Deepseek API | Rp 30.000 - 100.000 | Embeddings + chat ~$1-3/bulan |
| Groq API | GRATIS | Fallback untuk chat |
| Cloudflare Tunnel | GRATIS | Remote access |
| Domain | Rp 100.000 - 200.000/tahun | e.g. ai-posyandu.wonosobokab.go.id |
| SSL Certificate | GRATIS | Let's Encrypt |
| **Total** | **~Rp 250.000 - 650.000/bulan** | |

## 3.3 Estimasi Biaya Pengembangan

| Fase | Durasi | Biaya |
|------|--------|-------|
| Fase 1 (AI & RAG) | 2-3 minggu | Rp 1.500.000 |
| Fase 2 (Alert) | 2-3 minggu | Rp 1.500.000 |
| Fase 3 (Integrasi) | 3-4 minggu | Rp 2.500.000 |
| **Total** | **3-4 bulan** | **Rp 5.500.000** |

---

# BAB IV KEBERLANJUTAN

## 4.1 Rencana Handover

Setelah masa pilot berakhir:
1. **Transfer Knowledge** — Training intensif untuk tim teknis lokal
2. **Dokumentasi** — Dokumentasi lengkap sistem dalam bahasa Indonesia
3. **Source Code** — Commit ke repository dengan license yang sesuai
4. **Operasi** — Tim IT Dinas Kesehatan übernimmt operasional

## 4.2 Rencana Monitoring

| Aktivitas | Frekuensi | Penanggung Jawab |
|-----------|-----------|------------------|
| Review data Z-score | Bulanan | Bidan Desa |
| Evaluasi sistem | 3-bulanan | Dinas Kesehatan |
| Audit keamanan | 6-bulanan | Tim IT |
| Backup database | Harian | System Admin |

## 4.3 Metrix Keberhasilan

| Metric | Target | Cara Ukur |
|--------|--------|-----------|
| Reduction in stunting rate | > 10% per tahun | Z-score data comparison |
| Alert response time | < 24 jam | Dari detection → Kader action |
| Kader activation rate | > 90% | Posyandu aktif / total Posyandu |
| Parent engagement | > 50% | Warga yang rutin bawa anak ke Posyandu |
| Data accuracy | > 95% | Cross-check dengan petugas kesehatan |
| System uptime | > 99% | Monitoring |
| Cost per child tracked | < Rp 5.000/bulan | Total ops cost / anak |

## 4.4 Rencana Keberlanjutan Finansial

| Sumber Dana | Potensi |
|-------------|---------|
| Dinas Kesehatan Kabupaten | Budget kesehatan daerah |
| APBDes | Dana desa untuk Posyandu digital |
| CSR Perusahaan | Partnership dengan BCA/korporasi |
| Grants Nasional | Kemenkes, Bappenas innovation grants |

---

# BAB V PENUTUP

AI-Posyandu v1.5 sudah memiliki fondasi yang solid dengan chatbot Telegram, dashboard untuk berbagai level users, dan AI classifier untuk Z-score. Pengembangan ke v2.0 fokus pada:

1. **Semantic RAG** — AI chat yang sebenarnya memahami data Posyandu
2. **Auto-alert system** — deteksi dini balita berisiko tanpa perlu monitoring manual
3. **Visualisasi tren** — dashboard untuk tracking progress stunting
4. **Integrasi Faskes** — sinkronisasi data dengan Puskesmas

Dengan estimasi biaya Rp 250.000-650.000/bulan, sistem ini sangat feasible untuk Desa Patakbanteng dan bisa di-scale ke desa lain di Wonosobo.

**Langkah selanjutnya:** Persetujuan dari Dinas Kesehatan Kabupaten Wonosobo untuk pilot project 3 bulan, kemudian evaluasi dan pengembangan Fase 2.

---

# LAMPIRAN

## A. Link Sistem Berjalan
- Backend API: http://localhost:5001
- Dashboard: (Vercel deployment atau localhost:5173)

## B. Referensi
- WHO Child Growth Standards: https://www.who.int/tools/child-growth-standards
- Deepseek API: https://platform.deepseek.com
- Groq API: https://console.groq.com
- React: https://react.dev

## C. Contoh Knowledge Base untuk RAG
1. **PMBA (Pedoman Makan Bayi dan Balita)** — Kemenkes RI
2. **Standar WHO Z-Score** — tabel reference
3. **Panduan Stunting Prevensi** — strategi nasional
4. **Jadwal Imunisasi Nasional** — IDAI recommendations
5. **Resep MPASI Lokal** — makanan padat untuk bayi 6-12 bulan

## D. Teknologi Stack

| Layer | Teknologi | Version |
|-------|-----------|---------|
| Backend | Flask | 3.x |
| Bot | python-telegram-bot | 21.x |
| AI Chat | Deepseek v4-flash/pro | - |
| Database | SQLite + aiosqlite | 3.x |
| Frontend | React + Vite + Tailwind | React 18 |
| Scheduler | APScheduler | 3.x |
| Semantic Search | TF-IDF (numpy) | - |

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem AI-Posyandu v2.0*
*Versi: 2.0 | Tanggal: April 2026*
*Disusun untuk: Program Gerakan Berbakti*
