# PROPOSAL PENGEMBANGAN SISTEM
# AI-Posyandu v2.0 — Platform AI Agent untuk Pencegahan Stunting dan Aktivasi Posyandu

---

## 1. LATAR BELAKANG

AI-Posyandu adalah platform berbasis AI Agent yang dirancang untuk membantu pencegahan stunting dan aktivasi Posyandu di Desa Patakbanteng, Wonosobo, Jawa Tengah. Sistem ini terdiri dari Telegram Bot untuk interaksi warga, dashboard web untuk Kader/Bidan, dan AI reasoning untuk klasifikasi status gizi balita berdasarkan standar WHO.

**Kondisi Saat Ini (v1.0):**
- Telegram Bot sudah aktif untuk registrasi warga dan chat AI
- Dashboard React untuk Kader, Bidan, dan Kepala Desa
- AI BB/TB classifier berdasarkan standar WHO (Z-score)
- Database SQLite menyimpan data anak dan rekam medis
- Backend Flask dengan REST API
- Auto-notification dan reminder via Telegram

**Permasalahan yang Dihadapi:**
- AI chat masih berbasis keyword matching (LIKE query), bukan semantic search
- Tidak ada sistem RAG (Retrieval Augmented Generation) untuk jawaban berbasis data
- Dashboard belum memiliki visualisasi tren stunting per wilayah
- belum ada sistem alert otomatis untuk balita dengan Z-score berisiko
- belum ada integrasi dengan sistem Puskesmas/Faskes lain

---

## 2. CAPAIAN SAAT INI (v1.5)

### Sistem yang Sudah Berjalan

| Komponen | Status | Keterangan |
|----------|--------|------------|
| Telegram Bot | ✅ Aktif | @bot, registrasi, chat AI, reminder |
| Dashboard Kader | ✅ Aktif | React, statistik anak, input data |
| Dashboard Bidan | ✅ Aktif | Detail anak, rekam medis, klasifikasi |
| Dashboard Kepala Desa | ✅ Aktif | Overview seluruh desa, statistik |
| AI BB/TB Classifier | ✅ Aktif | WHO Z-score: -1 SD (normal), -3 SD to < -1 SD (risiko), < -3 SD (berat) |
| Auto-notification | ✅ Aktif | Reminder jadwal imunisasi via bot |
| Database | ✅ Aktif | SQLite, 100KB+ data anak |

### Teknologi yang Digunakan

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

## 3. RENCANA PENGEMBANGAN (v2.0)

### Fase 1 — AI & RAG Upgrade (2-3 minggu)

**3.1 Semantic Search dengan Embeddings**
- Upgrade dari keyword LIKE → semantic search menggunakan embeddings
- Deepseek embedding model (text-embedding-3-small atau model yang tersedia)
- Query: "anak dengan berat badan kurang" → tetap temukan "balita underweight" dsb

**3.2 RAG (Retrieval Augmented Generation)**
- AI chat mengambil konteks dari database sebelum menjawab
- Contoh: tanya "berapa anak Z-score merah?" → AI jawab berdasarkan data aktual
- Tidak lagi answer dari training data saja

**3.3 Knowledge Base Terstruktur**
- Dokumen: panduan PMBA (Pedoman Makan Bayi dan Balita), standar WHO, kebijakan stunting lokal
- Di-load ke vector store untuk retrieval
- AI bisa jawab pertanyaan spesifik tentang stunting prevention

---

### Fase 2 — Alert & Monitoring (2-3 minggu)

**3.4 Auto-Alert untuk Z-Score Berisiko**
- Sistem auto-detect balita dengan Z-score kuning/merah
- Notifikasi otomatis ke Kader dan Bidan via Telegram
- Alert level: 🟡 Risiko (home visit 7 hari) / 🔴 Berat (rujuk ke Puskesmas segera)

**3.5 Dashboard Tren Stunting**
- Visualisasi Z-score distribution per bulan
- Heatmap wilayah: mana dusun/RT yang paling banyak balita berisiko
- Perbandingan year-over-year progress

**3.6 Monitoring Kinerja Kader**
- Track: berapa banyak balita tiap Kader, compliance rate imunisasi
- Reminder otomatis jika ada balita belum ditimbang >1 bulan
- Leaderboard kebahagiaan (nutrition success rate)

---

### Fase 3 — Integrasi & Skalabilitas (3-4 minggu)

**3.7 Integrasi Puskesmas/Faskes**
- API untuk bidirectional data exchange dengan Puskesmas
- Rujukan otomatis: balita Z-score < -3 SD → kirim notifikasi ke Puskesmas
- Data imunisasi dari Faskes masuk ke sistem Posyandu

**3.8 Mobile App (React Native)**
- Aplikasi mobile untuk Kader下地
- Input data anthropometri langsung dari lapangan
- Camera capture untuk dokumentasi
- Offline-first dengan sync saat ada koneksi

**3.9 Multi-Desa Scaling**
- Sistem support multiple villages dengan satu dashboard
- Kepala Desa能看到各县的数据
- District-level aggregation untuk camat

**3.10 Laporan Otomatis ke Dinas Kesehatan**
- Generate laporan bulanan: jumlah balita, Z-score distribution, progress
- Export ke format yang dibutuhkan Dinas (CSV, Excel, PDF)
- Auto-submit via email atau API

---

## 4. ESTIMASI BIAYA OPERASI

| Komponen | Biaya/Bulan | Keterangan |
|----------|-------------|------------|
| VPS (server) | Rp 200.000 - 500.000 | Depends on specs needed |
| Deepseek API | Rp 30.000 - 100.000 | Embeddings + chat ~$1-3/bulan |
| Groq API | GRATIS | Fallback untuk chat |
| Cloudflare Tunnel | GRATIS | Remote access |
| Domain | Rp 100.000 - 200.000/tahun | e.g. ai-posyandu.wonosobokab.go.id |
| SSL Certificate | GRATIS | Let's Encrypt |
| **Total** | **~Rp 250.000 - 650.000/bulan** | |

---

## 5. TIM PENGEMBANG

| Peran | Tugas |
|-------|-------|
| Project Manager | Koordinasi dengan Dinas Kesehatan, monitoring |
| Backend Developer | Flask API, database, RAG implementation |
| Frontend Developer | React dashboard, mobile app |
| AI/ML Engineer | Embeddings, RAG pipeline, alert system |
| UI/UX Designer | Wireframe, mockup, user flow |
| System Admin | Server, deployment, monitoring |

**Estimasi tim minimal**: 2-3 orang (1 fullstack + 1 AI engineer + 1 designer)

---

## 6. METRIX KEBERHASILAN

| Metric | Target | Cara Ukur |
|--------|--------|-----------|
| Reduction in stunting rate | > 10% per tahun | Z-score data comparison |
| Alert response time | < 24 jam | Dari detection → Kader action |
| Kader activation rate | > 90% | Posyandu aktif / total Posyandu |
| Parent engagement | > 50% | Warga yang rutin bawa anak ke Posyandu |
| Data accuracy | > 95% | Cross-check dengan petugas kesehatan |
| System uptime | > 99% | Monitoring |
| Cost per child tracked | < Rp 5.000/bulan | Total ops cost / anak |

---

## 7. DOKUMENTASI TEKNIS

### Arsitektur Sistem v2.0

```
                        ┌──────────────────┐
                        │      Warga       │
                        │   (Telegram +    │
                        │    Mobile App)    │
                        └────────┬─────────┘
                                 │ message / http
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │  Telegram Bot     │  │   Flask API      │  │  React Frontend   │
  │  (Python/pytele)  │  │   (port 5001)  │  │  (port 5002)    │
  └────────┬─────────┘  └────────┬─────────┘  └──────────────────┘
           │                      │
           │ write/read           │ read/write
           ▼                      ▼
  ┌──────────────────────────────────────────────┐
  │              SQLite Database                    │
  │           (posyandu.db)                       │
  └──────────────────────────────────────────────┘
           │
           ├──────────────┐
           ▼              ▼
  ┌──────────────────┐  ┌──────────────────┐
  │  Deepseek API     │  │  WHO Z-Score     │
  │  (chat + embed)  │  │  Calculator      │
  └──────────────────┘  └──────────────────┘
           │
           ▼
  ┌──────────────────┐
  │  Vector Store     │
  │  (knowledge base) │
  └──────────────────┘
```

### AI-Posyandu Agent Personality

```
Nama: Nutri (AI Assistant)
Penampilan: Selalu hangat dan menyemangati, menggunakan emoji untuk data kesehatan anak
Sifat: Berbasis data, akurat, dengan sentuhan empathy Indonesia

Contoh respons:
"Bu, dari data kami, Adi (3 tahun) saat ini ada di Z-score -2.1 SD. 
Artinya perlu perhatian lebih ya. Saran kami: 
1) Kunjugi Posyandu minggu depan untuk pengukuran ulang 
2) Konsultasi ke Bidan untuk panduan makan siang
3) Makan makanan tinggi protein: telur, ikan, tempe 💪"

"Bu, bagus banget pertanyaan ibu! Untuk anak 6-12 bulan, 
WHO merekomendasikan: ASI eksklusif 6 bulan, 
lalu MPASI dimulai bertahap mulai 6 bulan. 
Kalau di daerah sini, kami sarankan: bubur hati ayam + puree buah 🥕"
```

### Database Schema

```sql
CREATE TABLE children (
    id INTEGER PRIMARY KEY,
    nama TEXT NOT NULL,
    tanggal_lahir TEXT,
    jenis_kelamin TEXT,
    nama_ortu TEXT,
    no_hp_ortu TEXT,
    alamat TEXT,
    dusun TEXT,
    rt TEXT,
    rw TEXT,
    berat_lahir REAL,
    panjang_lahir REAL,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE health_records (
    id INTEGER PRIMARY KEY,
    child_id INTEGER,
    tanggal TEXT,
    berat REAL,
    panjang REAL,
    lingkar_kepala REAL,
    z_score_bb_u REAL,
    z_score_pb_u REAL,
    z_score_bb_pb REAL,
    status_gizi TEXT,      -- Normal / Risiko / Berat
    catatan TEXT,
    created_at TEXT,
    FOREIGN KEY (child_id) REFERENCES children(id)
);

CREATE TABLE posyandu_schedules (
    id INTEGER PRIMARY KEY,
    tanggal TEXT,
    lokasi TEXT,
    dusun TEXT,
    jenis TEXT,            -- Umum / Bayi / Balita
    created_at TEXT
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    child_id INTEGER,
    notification_type TEXT,  -- reminder / alert / reminder_imunisasi
    message TEXT,
    sent_at TEXT,
    read_at TEXT,
    FOREIGN KEY (child_id) REFERENCES children(id)
);
```

### API Endpoints

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | /api/health | Health check |
| GET | /api/stats | Dashboard statistics |
| GET | /api/children | List all children |
| GET | /api/children/:id | Child detail + health records |
| POST | /api/children | Register new child |
| GET | /api/children/:id/health-records | Get health history |
| POST | /api/children/:id/health-record | Add health record + auto-classify Z-score |
| PATCH | /api/children/:id/health-record/:record_id | Update health record |
| POST | /api/agent/chat | AI Agent chat with RAG |
| GET | /api/agent/classify | Standalone Z-score classification |
| GET | /api/alerts | Get all active alerts (yellow/red Z-score) |
| GET | /api/alerts/child/:id | Get alerts for specific child |
| POST | /api/notifications/send | Send notification |
| GET | /api/posyandu/schedules | Get upcoming Posyandu schedules |
| GET | /api/posyandu/trends | Get Z-score trends over time |

---

## 8. JADWAL KERJA

| Bulan | Aktivitas |
|-------|-----------|
| Bulan 1 | Semantic search + RAG implementation + Knowledge base setup |
| Bulan 2 | Auto-alert system + Dashboard tren stunting |
| Bulan 3 | Monitoring kinerja Kader + Integrasi Puskesmas |
| Bulan 4 | Mobile app (React Native) + Multi-desa scaling |
| Bulan 5 | Laporan otomatis + Optimasi + User testing |
| Bulan 6 | Pilot evaluation + documentation + handover |

---

## 9. RISIKO DAN MITIGASI

| Risiko | Probabilitas | Mitigasi |
|--------|-------------|----------|
| AI hallucinate info kesehatan | Medium | RAG with verified WHO sources + disclaimer |
| Data warga tidak akurat | Medium | Cross-check dengan Bidan secara berkala |
| Kader tidak bisa pakai teknologi | Medium | Training + UI sederhana + offline-first |
| Internet di desa tidak stabil | High | Mobile app offline-first + sync when online |
| Privacy data kesehatan | High | Anonymize for reporting + consent from ortu |
| AI misclassify Z-score | Low | Double-check dengan rule-based WHO calculator |
| Server downtime | Low | Cloudflare Tunnel + auto-restart + monitoring |

---

## 10. KESIMPULAN

AI-Posyandu v1.5 sudah memiliki fondasi yang solid dengan chatbot Telegram, dashboard untuk berbagai level users, dan AI classifier untuk Z-score. Pengembangan ke v2.0 fokus pada:

1. **Semantic RAG** — AI chat yang sebenarnya memahami data Posyandu
2. **Auto-alert system** — deteksi dini balita berisiko tanpa perlu monitoring manual
3. **Visualisasi tren** — dashboard untuk tracking progress stunting
4. **Integrasi Faskes** — sinkronisasi data dengan Puskesmas

Dengan estimasi biaya Rp 250.000-650.000/bulan, sistem ini sangat feasible untuk Desa Patakbanteng dan bisa di-scale ke desa lain di Wonosobo.

**Langkah selanjutnya**: Persetujuan dari Dinas Kesehatan Kabupaten Wonosobo untuk pilot project 3 bulan, kemudian evaluasi dan pengembangan Fase 2.

---

## 11. LAMPIRAN

### A. Link Sistem Berjalan
- Backend API: http://localhost:5001
- Dashboard: (Vercel deployment atau localhost:5173)

### B. Referensi
- WHO Child Growth Standards: https://www.who.int/tools/child-growth-standards
- Deepseek API: https://platform.deepseek.com
- Groq API: https://console.groq.com
- React: https://react.dev

### C. Contoh Knowledge Base untuk RAG
1. **PMBA (Pedoman Makan Bayi dan Balita)** — Kemenkes RI
2. **Standar WHO Z-Score** — tabel reference
3. **Panduan Stunting Prevensi** — strategi nasional
4. **Jadwal Imunisasi Nasional** — IDAI recommendations
5. **Resep MPASI Lokal** — makanan padat untuk bayi 6-12 bulan

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem AI-Posyandu v2.0*
*Versi: 2.0 | Tanggal: 25 April 2026*
