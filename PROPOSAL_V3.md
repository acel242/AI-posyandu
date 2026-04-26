# FORMAT PROPOSAL PROGRAM BCA

---

# COVER

## AI-POSYANDU WONOSOBO v3.0
### Platform AI Agent untuk Pencegahan Stunting dan Aktivasi Posyandu

**Program:** Gerakan Berbakti untuk Indonesia Lebih Sehat  
**Lokasi:** Desa Patakbanteng, Kecamatan Kejajar, Kabupaten Wonosobo, Jawa Tengah  
**Tanggal:** April 2026  
**Versi:** 3.0  
**Status:** Draft untuk Persetujuan Dinas Kesehatan Kabupaten Wonosobo  

---

# HALAMAN IDENTITAS

| Field | Detail |
|-------|--------|
| **Nama Program** | AI-Posyandu Wonosobo |
| **Jenis Program** | Platform AI Agent untuk Kesehatan Masyarakat |
| **Lokasi Implementasi** | Desa Patakbanteng, Kecamatan Kejajar, Kabupaten Wonosobo, Jawa Tengah |
| **Durasi Program** | 4 Bulan (Pilot) |
| **Penanggung Jawab** | Tim Pengembangan AI-Posyandu |
| **Versi Dokumen** | 3.0 |
| **Tanggal** | 25 April 2026 |
| **Target Beneficiaries** | 50+ balita dan keluarga di Patakbanteng |
| **Anggaran Total** | Rp 5.500.000 |

---

# RINGKASAN

AI-Posyandu Wonosobo adalah platform berbasis AI Agent yang dirancang khusus untuk membantu pencegahan stunting dan aktivasi Posyandu di Desa Patakbanteng, Kecamatan Kejajar, Kabupaten Wonosobo, Jawa Tengah. Sistem ini terdiri dari Telegram Bot untuk interaksi warga, dashboard web untuk Kader/Bidan, dan AI reasoning untuk klasifikasi status gizi balita berdasarkan standar WHO.

## Permasalahan Utama

| No | Permasalahan | Dampak |
|----|-------------|--------|
| 1 | Stunting masih tinggi di Wonosobo | 1 dari 4 balita mengalami stunting |
| 2 | Monitoring balita manual tidak efisien | Kader kewalahan tracking ratusan anak |
| 3 | AI chat belum berbasis data | Jawaban tidak akurat karena tidak akses database |
| 4 | Tidak ada alert otomatis | Balita berisiko tidak terdeteksi sampai check-up berikutnya |
| 5 | Data tidak terintegrasi | Puskesmas dan Posyandu pakai sistem berbeda |

## Solusi yang Ditawarkan

AI-Posyandu Wonosobo menyediakan:
- **Telegram Bot (@ai_posyandu_bot)** — Chatbot AI untuk warga dengan akses data anak mereka
- **Dashboard Kader** — Input data anthropometri, lihat statistik
- **Dashboard Bidan** — Detail anak, rekam medis, klasifikasi Z-score
- **AI Chat with RAG** — AI yang benar-benar akses database untuk jawaban akurat
- **Auto-Alert System** — Notifikasi otomatis untuk balita Z-score berisiko
- **Semantic Search** — Cari anak berdasarkan kondisi, bukan NIK saja

## Angka Kunci

| Metric | Nilai |
|--------|-------|
| Total Balita Terdaftar | 50+ (pilot Patakbanteng) |
| Coverage Target | Seluruh Posyandu di Wonosobo |
| AI Accuracy | > 95% (Z-score calculation) |
| Alert Response Target | < 24 jam |
| Estimasi Biaya Bulanan | Rp 250.000 - 650.000 |
| Target Penurunan Stunting | > 10% per tahun |

## Permintaan Dana

| Fase | Durasi | Estimasi Biaya |
|------|--------|----------------|
| Fase 1 (AI & RAG) | 2-3 minggu | Rp 1.500.000 |
| Fase 2 (Alert & Monitoring) | 2-3 minggu | Rp 1.500.000 |
| Fase 3 (Integrasi & Skala) | 3-4 minggu | Rp 2.500.000 |
| **Total** | **3-4 bulan** | **Rp 5.500.000** |

---

# BAB I ANALISIS MASALAH

## 1.1 Latar Belakang

### 1.1.1 Stunting di Indonesia

Stunting adalah kondisi gagal tumbuh pada balita akibat kekurangan gizi kronis. Prevalensi stunting di Indonesia masih tinggi:

| Wilayah | Prevalensi Stunting |
|--------|-------------------|
| Nasional | 21,6% (SSGI 2023) |
| Jawa Tengah | 20,3% |
| Wonosobo | ~25% (di atas rata-rata nasional) |

### 1.1.2 Peran Posyandu

Posyandu (Pos Pelayanan Terpadu) adalah garda terdepan pemantauan tumbuh kembang balita di Indonesia. Fasilitas ini dijalankan oleh:
- **Kader Posyandu** — Volunteer masyarakat, dilatih untuk pengukuran dasar
- **Bidan Desa** — Tenaga kesehatan professional, menangani kasus berisiko
- **Kepala Desa** — Penanggung jawab wilayah

### 1.1.3 Permasalahan di Patakbanteng

**Geografis:**
- Desa di ketinggian (~900m dpl), akses ke Puskesmas jauh
- Banyak dusun terpencil dengan internet terbatas

**SDM:**
- Kader umumnya ibu-ibu rumah tangga, keterbatasan teknologi
- Bidan hanya 1 untuk beberapa desa

**Data:**
- Pencatatan masih manual di buku KIA
- Data tidak terstandarisasi antar Posyandu
- Tidak ada sistem alert untuk balita berisiko

## 1.2 Analisis Permasalahan

### Dari Sisi Warga

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Tidak tahu jadwal Posyandu | Perlu tanya kader setiap bulan | Tinggi |
| Tidak tahu status gizi anak | Tidak ada cara track mandiri | Tinggi |
| Bingung tanya soal nutrisi | Tidak ada yang bisa ditanya kapan saja | Sedang |
| Tidak ada reminder | Lupa jadwal penimbangan | Tinggi |
| Jarak ke Puskesmas jauh | Harus turun ke kecamatan untuk kasus serius | Tinggi |

### Dari Sisi Kader

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Buku KIA penuh | Catat manual, susah cari data lama | Tinggi |
| Tidak ada alarm untuk anak berisiko | Harus ingat sendiri mana anak bermasalah | Tinggi |
| Tidak ada feedback system | Tidak tahu apakah keluarga sudah intervention | Sedang |
| Training terbatas | Hanya diajari pengukuran, tidak analisis | Sedang |
| Workload tinggi | 1 kader handle 30-50 balita | Tinggi |

### Dari Sisi Bidan

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Data dari berbagai Posyandu tidak unify | Harus kumpulkan dari banyak buku | Tinggi |
| Tidak ada sistem alert | Tidak tahu balita baru masuk zona merah | Tinggi |
| Referral ke Puskesmas tidak trackable | Tidak tahu apakah keluarga sudah ke Puskesmas | Sedang |
| Laporan bulanan manual | Hitung manual, prone error | Tinggi |

## 1.3 Studi Kasus / Referensi

### Sistem Similar yang Sudah Ada

| Sistem | Lembaga | Kekuatan | Kelemahan |
|--------|---------|----------|----------|
| **SI-HEPI** | Kemenkes | Nationwide, data nasional | Tidak ada AI, UI kuno |
| **e-PPGBM** | Kemendagri | Untuk bidan desa | Kompleks, offline-first |
| **Posyandu Digital** | Startups | UX bagus | Tidak integrate dengan sistem pemerintah |
| **ASIK** | Bappenas | Integrasi data kesehatan | Rollout lambat |

### AI Health Assistants Worldwide

| Sistem | Negara | Teknologi | Hasil |
|--------|--------|-----------|-------|
| **Babylon Health** | UK | AI triage | 80% accuracy vs GP |
| **Ada Health** | Germany | AI symptom checker | 90% accuracy |
| **Khan Academy** | Global | AI tutor | Improves learning 2x |

## 1.4 Capaian Sistem Saat Ini (v1.5)

| Komponen | Status | Detail |
|----------|--------|--------|
| Telegram Bot | ✅ Aktif | Registrasi, chat AI, reminder |
| Dashboard Kader | ✅ Aktif | React, statistik, input data |
| Dashboard Bidan | ✅ Aktif | Detail anak, rekam medis |
| Dashboard Kepala Desa | ✅ Aktif | Overview statistik |
| AI BB/TB Classifier | ✅ Aktif | WHO Z-score standard |
| Auto-notification | ✅ Aktif | APScheduler reminder |
| Semantic Search (RAG) | ✅ Aktif | TF-IDF knowledge base |

---

# BAB II METODE PELAKSANAAN

## 2.1 Metode Pengumpulan Data

### Data Primer
- **Registrasi Warga:** Via Telegram Bot dengan validasi Kader
- **Pengukuran Anthropometri:** Input manual oleh Kader via dashboard
- **Chat Interaction:** Data percakapan AI untuk feedback loop

### Data Sekunder
- **Buku KIA** — Data historis balita dari catatan manual
- **Standar WHO** — Tabel Z-score untuk klasifikasi
- **PMBA (Pedoman Makan Bayi dan Balita)** — Kemenkes RI
- **Jadwal Imunisasi Nasional** — IDAI recommendations

## 2.2 Metode Analisis

### AI Z-Score Classification (WHO Standards)

| Status | Z-Score Range | Aksi |
|--------|---------------|------|
| 🟢 Normal | ≥ -1 SD | Rutin |
| 🟡 Risiko | -3 SD ≤ Z < -1 SD | Home visit 7 hari |
| 🔴 Berat | < -3 SD | Rujuk ke Puskesmas |

### RAG Pipeline (Retrieval Augmented Generation)

```
User Message → Semantic Search → Retrieve Context → Generate Response
```

### Knowledge Base untuk RAG
1. PMBA (Pedoman Makan Bayi dan Balita) — Kemenkes
2. Standar WHO Z-Score
3. Jadwal Imunisasi Nasional
4. Panduan Stunting Prevensi
5. Resep MPASI Lokal

## 2.3 Timeline Implementasi

| Minggu | Aktivitas | Output |
|--------|-----------|--------|
| 1 | Setup environment, migrate DB | Dev environment ready |
| 2-3 | RAG implementation, semantic search | AI chat works with data |
| 4 | Knowledge base population | PMBA, WHO loaded |
| 5 | Alert system + dashboard trends | Auto alerts working |
| 6 | Kader dashboard optimization | UI/UX improvements |
| 7 | Bidan dashboard + referral | Complete workflow |
| 8 | Testing + bug fixes | System stable |
| 9-12 | Pilot di Patakbanteng | Real user feedback |
| 13-16 | Evaluation + refinement | Ready for scale |

## 2.4 Teknologi yang Digunakan

| Layer | Teknologi | Version |
|-------|-----------|---------|
| Backend | Flask | 3.x |
| Bot | python-telegram-bot | 21.x |
| AI Chat | Deepseek v4-flash/pro | - |
| AI Fallback | Groq (llama-3.3-70b) | - |
| Database | SQLite + aiosqlite | 3.x |
| Frontend | React + Vite + Tailwind | React 18 |
| Scheduler | APScheduler | 3.x |
| Semantic Search | TF-IDF (numpy) | - |

## 2.5 Alur Proses Sistem

### Registrasi Anak Baru

```
[WARGA] → /daftar → [BOT] → Step: Nama, Tanggal Lahir, Gender → [DB Insert] → [KADER APPROVE] → ✅ Terdaftar
```

### Input Pengukuran Rutin

```
[KADER] → Input BB/PB → [SYSTEM Calculate Z-score] → [AI Classification] → [Store DB] → [Check Alert] → [Send Notif]
```

---

# BAB III PROGRAM KERJA & RENCANA ANGGARAN

## 3.1 Rencana Pengembangan v3.0

### Fase 1 — AI & RAG Upgrade (2-3 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| Semantic Search | Upgrade dari LIKE → embeddings TF-IDF | Critical |
| RAG Pipeline | AI chat dengan konteks dari database | Critical |
| Knowledge Base | PMBA, WHO standards, jadwal imunisasi | High |
| Feedback Loop | AI belajar dari konfirmasi kader | Medium |

### Fase 2 — Alert & Monitoring (2-3 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| Auto-Alert Z-Score | Notifikasi otomatis untuk balita berisiko | Critical |
| Dashboard Tren | Visualisasi Z-score bulanan | High |
| Reminder System | Auto-notif jadwal Posyandu | High |
| Growth Chart | PNG generation untuk Telegram | Medium |

### Fase 3 — Integrasi & Skala (3-4 minggu)

| Fitur | Deskripsi | Priority |
|-------|-----------|----------|
| API Puskesmas | Bidirectional sync dengan Faskes | High |
| Multi-Desa | Support beberapa village dalam 1 dashboard | Medium |
| Laporan Otomatis | Generate laporan bulanan untuk Dinas | High |
| Mobile App | React Native untuk Kader lapangan | Low |

## 3.2 Estimasi Biaya Operasional Bulanan

| Komponen | Biaya | Keterangan |
|----------|-------|------------|
| VPS Server | Rp 200.000 - 400.000 | 2 vCPU, 4GB RAM |
| Deepseek API | Rp 30.000 - 80.000 | ~500-1000 chat requests |
| Groq API | GRATIS | Free tier unlimited |
| Domain | Rp 100.000/tahun | ~Rp 8.000/bulan |
| Cloudflare Tunnel | GRATIS | Remote access |
| SSL | GRATIS | Let's Encrypt |
| **Total** | **Rp 250.000 - 500.000/bulan** | |

## 3.3 Biaya Pengembangan

| Fase | Durasi | Biaya |
|------|--------|-------|
| Fase 1 (AI & RAG) | 2-3 minggu | Rp 1.500.000 |
| Fase 2 (Alert) | 2-3 minggu | Rp 1.500.000 |
| Fase 3 (Integrasi) | 3-4 minggu | Rp 2.500.000 |
| **Total** | **3-4 bulan** | **Rp 5.500.000** |

## 3.4 ROI Estimation

| Benefit | Per Tahun |
|---------|-----------|
| Waktu kader hemat | ~500 jam × Rp 15.000 = Rp 7.500.000 |
| Deteksi dini stunting | Mengurangi biaya kesehatan ~Rp 2.000.000/balita |
| Efisiensi pelaporan | ~Rp 3.000.000/tahun |

## 3.5 Komponen AI-Posyandu

| Komponen | Deskripsi |
|----------|-----------|
| Chatbot Telegram | @ai_posyandu_bot - register, cek status, tanya AI |
| Dashboard Kader | Input data, statistik, alerts |
| Dashboard Bidan | Detail anak, rekam medis, klasifikasi |
| Dashboard Kepala Desa | Overview seluruh desa |
| AI with RAG | Chat yang akses database untuk jawaban akurat |
| Auto-Alert System | Notifikasi untuk balita berisiko |

---

# BAB IV KEBERLANJUTAN

## 4.1 Rencana Handover

Setelah masa pilot berakhir:
1. **Transfer Knowledge** — Training intensif untuk tim teknis lokal (Dinas Kesehatan IT)
2. **Dokumentasi** — Dokumentasi lengkap sistem dalam bahasa Indonesia
3. **Source Code** — Commit ke repository dengan dokumentasi lengkap
4. **Operasi** — Tim IT Dinas Kesehatan übernimmt operasional

## 4.2 Rencana Monitoring & Evaluasi

| Aktivitas | Frekuensi | Penanggung Jawab |
|-----------|-----------|------------------|
| Review data Z-score | Bulanan | Bidan Desa |
| Evaluasi sistem | 3-bulanan | Dinas Kesehatan |
| Audit keamanan | 6-bulanan | Tim IT |
| Backup database | Harian | System Admin |
| Pilot evaluation | Week 12 | Semua stakeholder |

## 4.3 Metrix Keberhasilan

| Metric | Baseline | Target | Cara Ukur |
|--------|----------|--------|-----------|
| Stunting rate reduction | ~25% | < 22.5% | SSGI comparison yearly |
| Alert response time | N/A | < 24 jam | System log timestamp |
| Kader activation | 60% | > 90% | % Posyandu aktif |
| Parent engagement | 30% | > 60% | % yang rutin cek status |
| Data accuracy | 80% | > 95% | Cross-check sample |
| System uptime | N/A | > 99% | Monitoring |
| Cost per child | N/A | < Rp 5.000/bulan | Total ops / anak |

## 4.4 Rencana Keberlanjutan Finansial

| Sumber Dana | Potensi |
|-------------|---------|
| Dinas Kesehatan Kabupaten | Budget kesehatan daerah |
| APBDes | Dana desa untuk Posyandu digital |
| CSR Perusahaan | Partnership dengan BCA/korporasi |
| Grants Nasional | Kemenkes, Bappenas innovation grants |

## 4.5 Pelatihan & Adaptasi Pengguna

| Peserta | Durasi | Materi |
|---------|--------|--------|
| Kader | 2 hari | Sistem, input data, baca growth chart |
| Bidan | 1 hari | Dashboard, analisis data, referral |
| Kepala Desa | Half day | Overview, baca laporan |
| Orang Tua | 1 sesi | Cara pakai Telegram bot |

### User Adoption Strategy
1. **Pilot group** — 10 keluarga volunteer di Patakbanteng
2. **Incentive** — Hadiah untuk keluarga yang rutin cek status
3. **Kader champion** — Pilih 1 kader entusiast sebagai early adopter
4. **Dropbox-style** — "Cek status anak Anda" jadi kebiasaan

## 4.6 Maintenance & Dukungan

| Channel | Untuk | Jam Operasional |
|---------|-------|-----------------|
| Telegram Group | Kader, Bidan | 08:00-17:00 WIB |
| WhatsApp Admin | Escalation | 24/7 untuk urgent |
| Email | Issues formal | Senin-Jumat |

### SLA

| Issue | Response Time | Resolution Time |
|-------|---------------|-----------------|
| Critical (system down) | 1 jam | 4 jam |
| High (feature broken) | 4 jam | 24 jam |
| Medium (UI bug) | 1 hari | 3 hari |
| Low (improvement) | 1 minggu | Sprint next |

## 4.7 Keamanan & Privasi Data

### Data Classification

| Data | Sensitivity | Protection |
|------|-------------|------------|
| Nama anak | Medium | Not shown publicly |
| Alamat | High | Only visible to kader/bidan |
| NIK | High | Encrypted in DB |
| Health records | Critical | Full access control |
| Parent phone | High | Not shown to others |

### Access Control

```
Warga (Parent)
  └── Lihat: anaknya sendiri saja
  └── Edit: data anaknya sendiri
  └── Tanya AI: hanya anaknya

Kader
  └── Lihat: semua anak di wilayahnya
  └── Edit: pengukuran baru
  └── Tanya AI: semua data wilayahnya

Bidan
  └── Lihat: semua anak di desanya
  └── Edit: semua data
  └── Rujuk: generate surat

Admin
  └── Full access
  └── Manage kaders
  └── View all data
```

### Privacy Measures

- **No PII in AI responses** — Address, phone, NIK tidak pernah di-echokan oleh AI
- **Parent telegram_id filter** — Semua query children di-filter otomatis
- **Consent required** — Orang tua harus setuju data anaknya dipakai
- **Data retention** — Data di-anonimisasi setelah 5 tahun

---

# BAB V PENUTUP

## 5.1 Kesimpulan

AI-Posyandu Wonosobo v3.0 adalah solusi komprehensif untuk masalah stunting di Desa Patakbanteng dengan fitur:

✅ **AI Chat with RAG** — Jawaban berbasis data aktual
✅ **Auto-Alert System** — Deteksi dini balita berisiko
✅ **Privacy-First Design** — Data aman, hanya owner yang bisa lihat
✅ **Cost-Effective** — Hanya Rp 250-500K/bulan
✅ **Scalable** — Bisa di-extend ke desa lain

## 5.2 Rekomendasi

1. **Approve pilot project** — Mulai 3 bulan di Patakbanteng
2. **Alokasikan budget** — Rp 5.500.000 untuk development
3. **Tunjuk counterpart** — Satu staff Dinas sebagai联络人
4. **Pilot evaluation** — Review setelah 3 bulan

## 5.3 Langkah Selanjutnya

| Aksi | Penanggung Jawab | Deadline |
|------|------------------|----------|
| Review proposal | Dinas Kesehatan | 1 minggu |
| Approve budget | Kepala Dinas | 2 minggu |
| Kickoff meeting | Semua stakeholder | 3 minggu |
| Dev start | Tim teknis | 4 minggu |

---

# LAMPIRAN

## A. Link Sistem Berjalan

- Backend API: http://localhost:5001
- Dashboard: http://localhost:5173

## B. Referensi Teknis

| Resource | Link |
|----------|------|
| WHO Child Growth Standards | https://www.who.int/tools/child-growth-standards |
| PMBA Kemenkes | https://ayosehat.kemkes.go.id |
| Deepseek API | https://platform.deepseek.com |
| Groq API | https://console.groq.com |
| React Documentation | https://react.dev |
| Flask Documentation | https://flask.palletsprojects.com |

## C. Glossary

| Term | Definition |
|------|------------|
| Stunting | Gagal tumbuh akibat kekurangan gizi kronis |
| Z-score | Standar deviasi dari median WHO |
| Posyandu | Pos Pelayanan Terpadu untuk ibu dan anak |
| Kader | Volunteer masyarakat di Posyandu |
| RAG | Retrieval Augmented Generation — AI dengan konteks |

## D. Kontak

| Peran | Nama | Kontak |
|-------|------|--------|
| Project Lead | (TBD) | - |
| Technical Lead | (TBD) | - |
| Dinas Kesehatan | (TBD) | - |

## E. Arsitektur Sistem

```
                         ┌───────────────────────────────────────┐
                         │           EXTERNAL SERVICES            │
                         │  • Telegram Bot API                   │
                         │  • Deepseek API (AI Chat)            │
                         │  • Groq API (Fallback AI)            │
                         │  • WHO Z-Score Standards             │
                         └───────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Flask)                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  REST API   │  │  AI Agent   │  │  Scheduler  │  │  Database   │     │
│  │  /api/*     │  │  (RAG+Chat) │  │  (APScheduler│  │  (SQLite)   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                           │
                    ▼                                           ▼
┌─────────────────────────────┐       ┌─────────────────────────────────────┐
│     TELEGRAM BOT            │       │         FRONTEND (React)             │
│  • Message Handler          │       │  • Dashboard Kader (port 5173)      │
│  • Conversation Flow        │       │  • Dashboard Bidan                   │
│  • Inline Button           │       │  • Dashboard Kepala Desa             │
│  • File Photo Handler      │       │  • Growth Chart Visualization        │
└─────────────────────────────┘       └─────────────────────────────────────┘
```

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem AI-Posyandu Wonosobo v3.0*
*Versi: 3.0 | Tanggal: 25 April 2026*
*Disusun untuk: Dinas Kesehatan Kabupaten Wonosobo*
|