# PROPOSAL PENGEMBANGAN SISTEM
# AI-Posyandu Wonosobo v3.0
## Platform AI Agent untuk Pencegahan Stunting dan Aktivasi Posyandu di Desa Patakbanteng, Kabupaten Wonosobo

---

**Versi Dokumen:** 3.0  
**Tanggal:** 25 April 2026  
**Penanggung Jawab:** Tim Pengembangan AI-Posyandu  
**Status:** Draft untuk Persetujuan Dinas Kesehatan Kabupaten Wonosobo

---

## DAFTAR ISI

1. [Ringkasan Eksekutif](#1-ringkesan-eksekutif)
2. [Latar Belakang & Permasalahan](#2-latar-belakang--permasalahan)
3. [Solusi yang Ditawarkan](#3-solusi-yang-ditawarkan)
4. [Capaian Sistem Saat Ini](#4-capaian-sistem-saat-ini)
5. [Rencana Pengembangan v3.0](#5-rencana-pengembangan-v30)
6. [Arsitektur Sistem](#6-arsitektur-sistem)
7. [Spesifikasi Teknis](#7-spesifikasi-teknis)
8. [Estimasi Biaya](#8-estimasi-biaya)
9. [Jadwal Implementasi](#9-jadwal-implementasi)
10. [Tim Pengembang](#10-tim-pengembang)
11. [Matriks Risiko & Mitigasi](#11-matriks-risiko--mitigasi)
12. [Keamanan & Privasi Data](#12-keamanan--privasi-data)
13. [Metrix Keberhasilan](#13-metrix-keberhasilan)
14. [Pelatihan & Adaptasi Pengguna](#14-pelatihan--adaptasi-pengguna)
15. [Maintenance & Dukungan](#15-maintenance--dukungan)
16. [Roadmap Masa Depan](#16-roadmap-masa-depan)
17. [Kesimpulan & Rekomendasi](#17-kesimpulan--rekomendasi)
18. [Lampiran](#18-lampiran)

---

## 1. RINGKASAN EKSEKUTIF

### 1.1 Gambaran Proyek

**AI-Posyandu Wonosobo** adalah platform berbasis AI Agent yang dirancang khusus untuk membantu pencegahan stunting dan aktivasi Posyandu di Desa Patakbanteng, Kecamatan Kejajar, Kabupaten Wonosobo, Jawa Tengah. Sistem ini terdiri dari Telegram Bot untuk interaksi warga, dashboard web untuk Kader/Bidan, dan AI reasoning untuk klasifikasi status gizi balita berdasarkan standar WHO.

### 1.2 Permasalahan Utama

| No | Permasalahan | Dampak |
|----|-------------|--------|
| 1 | Stunting masih tinggi di Wonosobo | 1 dari 4 balita mengalami stunting |
| 2 | Monitoring balita manual tidak efisien | Kader kewalahantracking ratusan anak |
| 3 | AI chat belum berbasis data | Jawaban tidak akurat karena tidak akses database |
| 4 | Tidak ada alert otomatis | Balita berisiko tidak terdeteksi sampai check-up berikutnya |
| 5 | Data tidak terintegrasi | Puskesmas dan Posyandu pakai sistem berbeda |

### 1.3 Solusi yang Ditawarkan

AI-Posyandu Wonosobo menyediakan:
- **Telegram Bot (@ai_posyandu_bot)** — Chatbot AI untuk warga dengan akses data自己的孩子
- **Dashboard Kader** — Input data anthropometri, lihat statistik
- **Dashboard Bidan** — Detail anak, rekam medis, klasifikasi Z-score
- **AI Chat with RAG** — AI yang benar-benar akses database untuk jawaban akurat
- **Auto-Alert System** — Notifikasi otomatis untuk balita Z-score berisiko
- **Semantic Search** — Cari anak berdasarkan kondisi, bukan NIK saja

### 1.4 Angka Kunci

| Metric | Nilai |
|--------|-------|
| Total Balita Terdaftar | 50+ (pilot Patakbanteng) |
| Coverage Target | Seluruh Posyandu di Wonosobo |
| AI Accuracy | > 95% (Z-score calculation) |
| Alert Response Target | < 24 jam |
| Estimasi Biaya Bulanan | Rp 250.000 - 650.000 |
| Target Penurunan Stunting | > 10% per tahun |

### 1.5 Permintaan Dana

| Fase | Durasi | Estimasi Biaya |
|------|--------|----------------|
| Fase 1 (AI & RAG) | 2-3 minggu | Rp 1.500.000 |
| Fase 2 (Alert & Monitoring) | 2-3 minggu | Rp 1.500.000 |
| Fase 3 (Integrasi & Skala) | 3-4 minggu | Rp 2.500.000 |
| **Total** | **3-4 bulan** | **Rp 5.500.000** |

---

## 2. LATAR BELAKANG & PERMASALAHAN

### 2.1 Latar Belakang

### 2.1.1 Stunting di Indonesia

Stunting adalah kondisi gagal tumbuh pada balita akibat kekurangan gizi kronis. Prevalensi stunting di Indonesia masih tinggi:

- ** Nasional: 21,6%** (SSGI 2023)
- **Jawa Tengah: 20,3%**
- **Wonosobo: ~25%** (di atas rata-rata nasional)

### 2.1.2 Peran Posyandu

Posyandu (Pos Pelayanan Terpadu) adalah garda terdepan pemantauan tumbuh kembang balita di Indonesia. Fasilitas ini dijalankan oleh:
- **Kader Posyandu** — Volunteer masyarakat, dilatih untuk pengukuran dasar
- **Bidan Desa** — Tenaga kesehatan professional, menangani kasus berisiko
- **Kepala Desa** — Penanggung jawab wilayah

### 2.1.3 Permasalahan di Patakbanteng

**Geografis:**
- Desa di ketinggian (~900m dpl), akses ke Puskesmas jauh
- Banyak dusun terpencil dengan internet terbatas

** SDM:**
- Kader umumnya ibu-ibu rumah tangga, keterbatasan teknologi
- Bidan hanya 1 untuk beberapa desa

** Data:**
- Pencatatan masih manual di buku KIA
- Data tidak terstandarisasi antar Posyandu
- Tidak ada sistem alert untuk balita berisiko

### 2.2 Analisis Permasalahan

#### 2.2.1 Dari Sisi Warga

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Tidak tahu jadwal Posyandu | Perlu tanya kader setiap bulan | Tinggi |
| Tidak tahu status gizi anak | Tidak ada cara track mandiri | Tinggi |
| Bingung tanya soal nutrisi | Tidak ada yang bisa ditanya kapan saja | Sedang |
| Tidak ada reminder | Lupa jadwal penimbangan | Tinggi |
| Jarak ke Puskesmas jauh | Harus turun ke kecamatan untuk kasus serius | Tinggi |

#### 2.2.2 Dari Sisi Kader

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Buku KIA penuh | Catat manual, susah cari data lama | Tinggi |
| Tidak ada alarm untuk anak berisiko | Harus ingat sendiri mana anak bermasalah | Tinggi |
| Tidak tahu apakah keluarga sudah intervention | Tidak ada feedback system | Sedang |
| Training terbatas | Hanya diajari pengukuran, tidak analisis | Sedang |
| Workload tinggi | 1 kader handle 30-50 balita | Tinggi |

#### 2.2.3 Dari Sisi Bidan

| Permasalahan | Contoh | Frekuensi |
|-------------|--------|-----------|
| Data dari berbagai Posyandu tidak unify | Harus kumpulkan dari banyak buku | Tinggi |
| Tidak ada sistem alert | Tidak tahu balita baru masuk zona merah | Tinggi |
| Referral ke Puskesmas tidak trackable | Tidak tahu apakah keluarga sudah ke Puskesmas | Sedang |
| Laporan bulanan manual | Hitung manual, prone error | Tinggi |

### 2.3 Studi Kasus / Referensi

#### 2.3.1 Sistem Similar yang Sudah Ada

| Sistem | Lembaga | Kekuatan | Kelemahan |
|--------|---------|----------|----------|
| **SI-HEPI** | Kemenkes | Nationwide, data nasional | Tidak ada AI, UI kuno |
| **e-PPGBM** | Kemendagri | Untuk bidan desa | Kompleks, offline-first |
| **Posyandu Digital** | Startups | UX bagus | Tidak integrate dengan sistem pemerintah |
| **ASIK** | Bappenas | Integrasi data kesehatan | Rollout lambat |

#### 2.3.2 AI Health Assistants Worldwide

| Sistem | Negara | Teknologi | Hasil |
|--------|--------|-----------|-------|
| **Babylon Health** | UK | AI triage | 80% accuracy vs GP |
| **Ada Health** | Germany | AI symptom checker | 90% accuracy |
| **Khan Academy** | Global | AI tutor | Improves learning 2x |

### 2.4 Justifikasi Proyek

| Kriteria | Penilaian |
|----------|-----------|
| Kebutuhan pengguna | Tinggi — semua stakeholder punya masalah berbeda |
| Dampak sosial | Sangat Tinggi — menurunkan stunting = generasi lebih sehat |
| Efisiensi pemerintah | Tinggi — otomatisasi mengurangi beban kerja |
| Feasibility teknis | Tinggi — AI sudah mature, Z-score calculation straightforward |
| Efisiensi biaya | Tinggi — Rp 250-650K/bulan sangat terjangkau |
| Compliance | Tinggi — follow standar WHO dan kebijakan nasional |

---

## 3. SOLUSI YANG DITAWARKAN

### 3.1 Gambaran Solusi

AI-Posyandu Wonosobo adalah ekosistem terintegrasi yang menghubungkan warga, kader, bidan, dan pemerintah dalam satu platform:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI-POSYANDU WONOSOBO                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐ │
│   │    WARGA     │         │   AI ENGINE  │         │    KADER     │ │
│   │              │         │              │         │              │ │
│   │ • Telegram   │────────▶│ • RAG Chat   │◀────────│ • Dashboard  │ │
│   │ • Tanya AI   │         │ • Z-Score    │         │ • Input Data │ │
│   │ • Reminder   │         │ • Semantic    │         │ • Stats      │ │
│   └──────────────┘         └──────────────┘         └──────────────┘ │
│          │                        │                        │        │
│          │                        │                        │        │
│          ▼                        ▼                        ▼        │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                    FLASK API (Backend)                        │   │
│   │  • REST Endpoints  • SQLite DB  • Auth  • Scheduler          │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                              │                                        │
│                              ▼                                        │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │              SQLite Database (posyandu.db)                     │   │
│   │  • Children  • Health Records  • Schedules  • Alerts         │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                              │                                        │
│                              ▼                                        │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │              Vector Store (TF-IDF Semantic Search)             │   │
│   │  • Agent Lessons  • Knowledge Base                            │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Komponen Utama

#### 3.2.1 Chatbot Telegram AI

**Bot:** @ai_posyandu_bot

**Fitur:**
- `/start` — Welcome + menu utama
- `/daftar` — Register anak baru (warga)
- `/cek [NIK]` — Lihat status anak
- `/jadwal` — Lihat jadwal Posyandu
- `/tips [topik]` — Tips nutrisi dari knowledge base
- Natural Language — Tanya dalam bahasa Indonesia

**AI Personality (Nutri):**
```
"Bu, saya Nutri, asisten Posyandu AI Anda. Saya bisa bantu:
• Cek status gizi anak Anda
• Jawab pertanyaan tentang nutrisi
• Ingatkan jadwal Posyandu
• Beri tips MPASI yang lezat dan bergizi! 💪"
```

**Privacy:** AI hanya bisa akses data anak yang di-register oleh user tersebut (parent_telegram_id filter).

#### 3.2.2 Dashboard Kader

**Halaman:**
1. **Dashboard** — Statistik Posyandu, recent activity
2. **Anak** — List semua anak, filter by status
3. **Tambah Data** — Input pengukuran baru
4. **Jadwal** — Kelola jadwal Posyandu
5. **Alert** — List balita berisiko

**Fitur:**
- Quick search anak
- Bulk input pengukuran
- Growth chart visualization
- Export laporan

#### 3.2.3 Dashboard Bidan

**Halaman:**
1. **Overview** — Statistik seluruh desa
2. **Anak Detail** — Rekam medis lengkap
3. **Klasifikasi** — Z-score calculator standalone
4. **Rujukan** — Generate surat rujukan ke Puskesmas
5. **Laporan** — Bulanan/yearly reports

**Fitur:**
- AI-assisted analysis
- Photo documentation
- Referral tracking
- Historical comparison

#### 3.2.4 AI with RAG (Retrieval Augmented Generation)

**Flow:**
```
Warga: "Berapa anak Z-score merah di Posyandu saya?"
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  1. Semantic Search       │
                    │  Query: "Z-score merah"   │
                    │  → database query         │
                    └────────────┬──────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  2. Retrieve Context      │
                    │  → children WHERE         │
                    │    risk_status = 'red'    │
                    └────────────┬──────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  3. Generate Response     │
                    │  → Deepseek with context  │
                    └────────────┬──────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  4. Formatted Answer      │
                    │  "Ada 3 anak dengan      │
                    │   Z-score merah..."       │
                    └───────────────────────────┘
```

**Knowledge Base:**
1. PMBA (Pedoman Makan Bayi dan Balita) — Kemenkes
2. Standar WHO Z-Score
3. Jadwal Imunisasi Nasional
4. Panduan Stunting Prevensi
5. Resep MPASI Lokal

#### 3.2.5 Auto-Alert System

**Alert Levels:**

| Level | Kondisi | Aksi |
|-------|---------|------|
| 🟡 **Risiko** | -3 SD ≤ Z-score < -1 SD | Reminder ke orang tua + jadwal home visit |
| 🔴 **Berat** | Z-score < -3 SD | Auto-notif ke Bidan + suggest rujuk ke Puskesmas |
| ⚪ **Unmeasured** | > 1 bulan tidak ada data | Reminder ke orang tua |

**Notification Flow:**
```
[System detects Z-score merah]
    │
    ▼
[Create alert record]
    │
    ├──▶ Telegram message ke orang tua
    │    "Bu, anak Anda (Nama) perlu perhatian khusus..."
    │
    └──▶ Telegram message ke Bidan
         "Bidan, ada balita Z-score merah di Patakbanteng:
          Nama: X, Z-score: -3.2, Alamat: Y"
```

### 3.3 Alur Proses Lengkap

#### 3.3.1 Registrasi Anak Baru

```
[WARGA]                         [BOT/SYSTEM]                      [KADER]
   │                                  │                                │
   │  /daftar                        │                                │
   │────────────────────────────────▶│                                │
   │                                  │  "Mulai registrasi..."        │
   │                                  │  Step 1: Nama anak            │
   │◀────────────────────────────────│                                │
   │  "Nama lengkap anak?"            │                                │
   │──────────────────────────────────│                                │
   │                                  │  Step 2: Tanggal lahir         │
   │◀────────────────────────────────│                                │
   │  "Tanggal lahir?"                │                                │
   │──────────────────────────────────│                                │
   │                                  │  Step 3: Gender               │
   │◀────────────────────────────────│                                │
   │                                  │  ...continue...               │
   │                                  │                                │
   │                                  │  4. Insert to DB              │
   │                                  │───────────────────────────────▶│
   │                                  │                                │
   │                                  │  "Konfirmasi dari Kader?"      │
   │                                  │◀───────────────────────────────│
   │                                  │  [Kader approve via dashboard] │
   │                                  │                                │
   │  ✅ "Anak berhasil terdaftar!"   │                                │
   │◀────────────────────────────────│                                │
   ▼                                  ▼                                ▼
```

#### 3.3.2 Input Pengukuran Rutin

```
[KADER]                          [SYSTEM]                          [AI]
   │                                │                                 │
   │  Input: BB=8.5kg, PB=72cm     │                                 │
   │  untuk anak NIK: XXX          │                                 │
   │────────────────────────────────▶│                                 │
   │                                │  Calculate Z-score              │
   │                                │  WHO BB/TB formula              │
   │                                │────────────────────────────────▶│
   │                                │                                 │
   │                                │  Z-score = -1.8 SD (Risiko)    │
   │                                │◀────────────────────────────────│
   │                                │                                 │
   │  Show: 🟡 Z-score -1.8        │  Store to DB                   │
   │◀────────────────────────────────│                                 │
   │                                │                                 │
   │  [System check alert]          │                                 │
   │                                │  Z-score kuning → create alert  │
   │                                │  → Notif ke orang tua          │
   │                                │  → Notif ke Bidan              │
   │                                │                                 │
   ▼                                ▼                                 ▼
```

---

## 4. CAPAIAN SISTEM SAAT INI

### 4.1 Status Komponen

| Komponen | Status | Detail |
|----------|--------|--------|
| Telegram Bot | ✅ Aktif | Registrasi, chat AI, reminder |
| Dashboard Kader | ✅ Aktif | React, statistik, input data |
| Dashboard Bidan | ✅ Aktif | Detail anak, rekam medis |
| Dashboard Kepala Desa | ✅ Aktif | Overview statistik |
| AI BB/TB Classifier | ✅ Aktif | WHO Z-score standard |
| Auto-notification | ✅ Aktif | APScheduler reminder |
| Semantic Search (RAG 1.3.5 Privacy-First Design

**Self:** Anak hanya bisa Dilihat oleh:
- Orang tua (parent_telegram_id match)
- Kader yang注册的
- Bidan 풀어
- Admin 시스템

**AI Chat:** Tidak boleh akses data anak orang lain

---

## 5. RENCANA PENGEMBANGAN v3.0

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

---

## 6. ARSITEKTUR SISTEM

### 6.1 Arsitektur Overall

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

### 6.2 Database Schema

```sql
-- Children (balita)
CREATE TABLE children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nik TEXT UNIQUE,
    nama TEXT NOT NULL,
    tanggal_lahir TEXT,
    jenis_kelamin TEXT,           -- 'L' / 'P'
    parent_name TEXT,
    parent_phone TEXT,
    parent_telegram_id TEXT,
    address TEXT,
    dusun TEXT,
    rt TEXT,
    rw TEXT,
    berat_lahir REAL,
    panjang_lahir REAL,
    risk_status TEXT DEFAULT 'unmeasured',  -- green/yellow/red/unmeasured
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health Records (pengukuran)
CREATE TABLE health_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER REFERENCES children(id),
    tanggal TEXT,                  -- YYYY-MM-DD
    age_months INTEGER,           -- Umur dalam bulan
    berat REAL,                    -- Berat dalam kg
    panjang REAL,                  -- Panjang dalam cm
    lingkar_kepala REAL,
    z_score_bb_u REAL,            -- Weight-for-age Z-score
    z_score_pb_u REAL,            -- Height-for-age Z-score
    z_score_bb_pb REAL,           -- Weight-for-height Z-score
    bb_u_status TEXT,             -- Normal/Risiko/Berat
    pb_u_status TEXT,
    bb_pb_status TEXT,
    overall_status TEXT,           -- Final risk assessment
    classifier_ai TEXT,           -- 'Deepseek' / 'Rule-based'
    catatan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posyandu Schedules
CREATE TABLE posyandu_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheduled_date TEXT,
    scheduled_time TEXT,
    title TEXT,
    description TEXT,
    location TEXT,
    dusun TEXT,
    target_role TEXT DEFAULT 'semua',  -- warga/kader/bidan/semua
    created_by_telegram_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER REFERENCES children(id),
    alert_type TEXT,               -- 'zscore_red' / 'zscore_yellow' / 'unmeasured'
    alert_level TEXT,              -- 'red' / 'yellow' / 'info'
    message TEXT,
    is_resolved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Notifications
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER REFERENCES children(id),
    recipient_telegram_id TEXT,
    notification_type TEXT,        -- 'reminder' / 'alert' / 'reminder_imunisasi'
    message TEXT,
    sent_at TIMESTAMP,
    read_at TIMESTAMP
);

-- Conversation History (untuk context AI)
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT,
    child_id INTEGER,
    role TEXT,                    -- 'user' / 'assistant'
    message TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent Lessons (RAG knowledge base)
CREATE TABLE agent_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT,
    lesson_text TEXT,
    action_taken TEXT,
    outcome TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kaders
CREATE TABLE kaders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    telegram_id TEXT,
    role TEXT,                    -- 'kader' / 'bidan' / 'kepala_desa'
    dusun TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.3 AI Agent Flow

```
User Message
     │
     ▼
┌─────────────────────────────┐
│  1. Load Conversation      │
│  (last 5 messages)         │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  2. Check Tool Needed?     │
│  TOOLS: list_children,     │
│  get_child, classify, etc   │
└─────────────────────────────┘
     │
     ├──▶ YES ──▶ Execute Tool
     │                  │
     │                  ▼
     │         ┌─────────────────┐
     │         │  Inject         │
     │         │  _telegram_id   │
     │         │  (auth filter)  │
     │         └─────────────────┘
     │                  │
     │                  ▼
     │         ┌─────────────────┐
     │         │  Query Database │
     │         │  (filtered by   │
     │         │   telegram_id)  │
     │         └─────────────────┘
     │                  │
     │◀─────────────────┘
     │
     ├──▶ NO ──▶ Direct Response
     │
     ▼
┌─────────────────────────────┐
│  3. Call Deepseek API     │
│  (with context)           │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  4. Save to Conversation   │
│  & Return Response         │
└─────────────────────────────┘
```

---

## 7. SPESIFIKASI TEKNIS

### 7.1 Technology Stack

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

### 7.2 API Endpoints

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| GET | /api/health | Health check | None |
| GET | /api/stats | Dashboard statistics | None |
| GET | /api/children | List children (filtered by parent) | Telegram ID |
| GET | /api/children/:id | Child detail | Owner/Bidan |
| POST | /api/children | Register new child | Telegram ID |
| GET | /api/children/:id/health-records | Health history | Owner/Bidan |
| POST | /api/children/:id/health-record | Add measurement | Kader |
| PATCH | /api/children/:id/health-record/:rid | Update record | Kader |
| POST | /api/agent/chat | AI chat with RAG | Telegram ID |
| GET | /api/agent/classify | Standalone Z-score | None |
| GET | /api/agent/lessons | Search lessons | Admin |
| GET | /api/alerts | Active alerts | Kader/Bidan |
| POST | /api/notifications/send | Send notif | System |
| GET | /api/posyandu/schedules | List schedules | None |
| POST | /api/posyandu/schedules | Create schedule | Kader |
| GET | /api/kaders | List kaders | Admin |

### 7.3 WHO Z-Score Classification

| Status | Z-Score Range | Aksi |
|--------|---------------|------|
| 🟢 Normal | ≥ -1 SD | Rutin |
| 🟡 Risiko | -3 SD ≤ Z < -1 SD | Home visit 7 hari |
| 🔴 Berat | < -3 SD | Rujuk ke Puskesmas |

### 7.4 Security Measures

| Measure | Implementation |
|---------|----------------|
| Data Isolation | Children filtered by telegram_id |
| Admin Auth | ADMIN_USER_IDS env variable |
| Input Validation | All inputs sanitized |
| Rate Limiting | Via Telegram Bot API limits |
| No PII in Logs | Sensitive data masked |
| HTTPS Only | Via Cloudflare Tunnel |

---

## 8. ESTIMASI BIAYA

### 8.1 Biaya Operasional Bulanan

| Komponen | Biaya | Keterangan |
|----------|-------|------------|
| VPS Server | Rp 200.000 - 400.000 | 2 vCPU, 4GB RAM |
| Deepseek API | Rp 30.000 - 80.000 | ~500-1000 chat requests |
| Groq API | GRATIS | Free tier unlimited |
| Domain | Rp 100.000/tahun | ~Rp 8.000/bulan |
| Cloudflare Tunnel | GRATIS | Remote access |
| SSL | GRATIS | Let's Encrypt |
| **Total** | **Rp 250.000 - 500.000/bulan** | |

### 8.2 Biaya Pengembangan

| Fase | Durasi | Biaya |
|------|--------|-------|
| Fase 1 (AI & RAG) | 2-3 minggu | Rp 1.500.000 |
| Fase 2 (Alert) | 2-3 minggu | Rp 1.500.000 |
| Fase 3 (Integrasi) | 3-4 minggu | Rp 2.500.000 |
| **Total** | **3-4 bulan** | **Rp 5.500.000** |

### 8.3 ROI Estimation

| Benefit | Per Tahun |
|---------|-----------|
| Waktu kader hemat | ~500 jam × Rp 15.000 = Rp 7.500.000 |
| Deteksi dini stunting | Mengurangi biaya kesehatan ~Rp 2.000.000/balita |
| Efisiensi pelaporan | ~Rp 3.000.000/tahun |

---

## 9. JADWAL IMPLEMENTASI

### 9.1 Timeline

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

### 9.2 Milestones

| Milestone | Target | Criteria |
|-----------|--------|----------|
| M1: RAG Ready | Week 3 | AI bisa jawab "berapa anak Z-score merah?" |
| M2: Alert Active | Week 5 | Notifikasi terkirim untuk balita berisiko |
| M3: Dashboard Complete | Week 7 | Semua role bisa pakai sistem |
| M4: Pilot Done | Week 12 | 20+ families aktif |
| M5: Scale Ready | Week 16 | Siap untuk desa lain |

---

## 10. TIM PENGEMBANG

### 10.1 Struktur Tim

| Peran | Jumlah | Responsibility |
|-------|--------|----------------|
| Project Manager | 1 | Koordinasi, timeline, pelaporan |
| Fullstack Developer | 1 | Flask API, database, integrations |
| Frontend Developer | 1 | React dashboards |
| AI/ML Engineer | 1 | RAG pipeline, semantic search |
| UI/UX Designer | 1 | Wireframe, mockup, user flow |
| System Admin | 1 (part-time) | Server, deployment, monitoring |

### 10.2 Effort Estimation

| Aktivitas | Person-days |
|-----------|-------------|
| Backend development | 30 |
| Frontend development | 25 |
| AI/RAG development | 20 |
| Testing & QA | 15 |
| Deployment & monitoring | 10 |
| Documentation | 10 |
| **Total** | **110 person-days** |

---

## 11. MATRIKS RISIKO & MITIGASI

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AI hallucinate health advice | Medium | High | RAG with verified sources + disclaimer |
| Data warga bocor | Low | Critical | Encryption + access control |
| Kader tidak bisa pakai tech | Medium | Medium | Training + simple UI |
| Internet tidak stabil | High | Medium | Offline-first mobile app |
| AI miscalculate Z-score | Low | High | Double-check with rule-based |
| Low user adoption | Medium | Medium | Training + incentive program |
| Server downtime | Low | Medium | Auto-restart + monitoring |
| API cost overrun | Low | Low | Budget alert + Groq fallback |

---

## 12. KEAMANAN & PRIVASI DATA

### 12.1 Data Classification

| Data | Sensitivity | Protection |
|------|-------------|------------|
| Nama anak | Medium | Not shown publicly |
| Alamat | High | Only visible to kader/bidan |
| NIK | High | Encrypted in DB |
| Health records | Critical | Full access control |
| Parent phone | High | Not shown to others |

### 12.2 Access Control

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

### 12.3 Privacy Measures

- **No PII in AI responses** — Address, phone, NIK tidak pernah di-echokan oleh AI
- **Parent telegram_id filter** — Semua query children di-filter otomatis
- **Consent required** — Orang tua harus setuju data anaknya dipakai
- **Data retention** — Data di-anonimisasi setelah 5 tahun

---

## 13. METRIX KEBERHASILAN

| Metric | Baseline | Target | Cara Ukur |
|--------|----------|--------|-----------|
| Stunting rate reduction | ~25% | < 22.5% | SSGI comparison yearly |
| Alert response time | N/A | < 24 jam | System log timestamp |
| Kader activation | 60% | > 90% | % Posyandu aktif |
| Parent engagement | 30% | > 60% | % yang rutin cek status |
| Data accuracy | 80% | > 95% | Cross-check sample |
| System uptime | N/A | > 99% | Monitoring |
| Cost per child | N/A | < Rp 5.000/bulan | Total ops / anak |

---

## 14. PELATIHAN & ADAPTASI PENGGUNA

### 14.1 Training Program

| Peserta | Durasi | Materi |
|---------|--------|--------|
| Kader | 2 hari | Sistem, input data, baca growth chart |
| Bidan | 1 hari | Dashboard, analisis data, referral |
| Kepala Desa | Half day | Overview, baca laporan |
| Orang Tua | 1 sesi | Cara pakai Telegram bot |

### 14.2 User Adoption Strategy

1. **Pilot group** — 10 keluarga volunteer di Patakbanteng
2. **Incentive** — Hadiah untuk keluarga yang

### 14.2 User Adoption Strategy

1. **Pilot group** — 10 keluarga volunteer di Patakbanteng
2. **Incentive** — Hadiah untuk keluarga yang rutin cek status
3. **Kader champion** — Pilih 1 kader entusiast sebagai early adopter
4. **Dropbox-style** — "Cek status anak Anda" jadi kebiasaan

---

## 15. MAINTENANCE & DUKUNGAN

### 15.1 Support Channels

| Channel | Untuk | Jam Operasional |
|---------|-------|-----------------|
| Telegram Group | Kader, Bidan | 08:00-17:00 WIB |
| WhatsApp Admin | Escalation | 24/7 untuk urgent |
| Email | Issues formal | Senin-Jumat |

### 15.2 SLA

| Issue | Response Time | Resolution Time |
|-------|---------------|-----------------|
| Critical (system down) | 1 jam | 4 jam |
| High (feature broken) | 4 jam | 24 jam |
| Medium (UI bug) | 1 hari | 3 hari |
| Low (improvement) | 1 minggu | Sprint next |

### 15.3 Maintenance Routine

- **Daily** — Check uptime, monitor API costs
- **Weekly** — Backup database, review logs
- **Monthly** — Security audit, dependency update
- **Quarterly** — Performance review, feature planning

---

## 16. ROADMAP MASA DEPAN

### 16.1 v4.0 (6-12 bulan)

| Feature | Description |
|---------|-------------|
| Multi-language | Bahasa Jawa, Sunda, dll |
| Video Call | Konsultasi jarak jauh dengan bidan |
| Wearable Integration | Data dari smart scale/baby monitor |
| Blockchain Audit | Immutable log untuk compliance |

### 16.2 v5.0 (12-18 bulan)

| Feature | Description |
|---------|-------------|
| Provincial Scale | Rollout ke seluruh Wonosobo |
| Government Integration | API ke Dinas Kesehatan |
| ML Prediction | Prediksi risiko stunting sebelum born |

---

## 17. KESIMPULAN & REKOMENDASI

### 17.1 Kesimpulan

AI-Posyandu Wonosobo v3.0 adalah solusi komprehensif untuk masalah stunting di Desa Patakbanteng dengan fitur:

✅ **AI Chat with RAG** — Jawaban berbasis data aktual
✅ **Auto-Alert System** — Deteksi dini balita berisiko
✅ **Privacy-First Design** — Data aman, hanya owner yang bisa lihat
✅ **Cost-Effective** — Hanya Rp 250-500K/bulan
✅ **Scalable** — Bisa di-extend ke desa lain

### 17.2 Rekomendasi

1. **Approve pilot project** — Mulai 3 bulan di Patakbanteng
2. **Alokasikan budget** — Rp 5.500.000 untuk development
3. **Tunjuk counterpart** — Satu staff Dinas sebagai联络人
4. **Pilot evaluation** — Review setelah 3 bulan

### 17.3 Langkah Selanjutnya

| Aksi | Penanggung Jawab | Deadline |
|------|------------------|----------|
| Review proposal | Dinas Kesehatan | 1 minggu |
| Approve budget | Kepala Dinas | 2 minggu |
| Kickoff meeting | Semua stakeholder | 3 minggu |
| Dev start | Tim teknis | 4 minggu |

---

## 18. LAMPIRAN

### A. Link Sistem Berjalan

- Backend API: http://localhost:5001
- Dashboard: http://localhost:5173

### B. Referensi Teknis

| Resource | Link |
|----------|------|
| WHO Child Growth Standards | https://www.who.int/tools/child-growth-standards |
| PMBA Kemenkes | https://ayosehat.kemkes.go.id |
| Deepseek API | https://platform.deepseek.com |
| Groq API | https://console.groq.com |
| React Documentation | https://react.dev |
| Flask Documentation | https://flask.palletsprojects.com |

### C. Glossary

| Term | Definition |
|------|------------|
| Stunting | Gagal tumbuh akibat kekurangan gizi kronis |
| Z-score | Standar deviasi dari median WHO |
| Posyandu | Pos Pelayanan Terpadu untuk ibu dan anak |
| Kader | Volunteer masyarakat di Posyandu |
| RAG | Retrieval Augmented Generation — AI dengan konteks |

### D. Kontak

| Peran | Nama | Kontak |
|-------|------|--------|
| Project Lead | (TBD) | - |
| Technical Lead | (TBD) | - |
| Dinas Kesehatan | (TBD) | - |

---

*Dokumen ini dibuat sebagai proposal pengembangan sistem AI-Posyandu Wonosobo v3.0*
*Versi: 3.0 | Tanggal: 25 April 2026*
*Disusun untuk: Dinas Kesehatan Kabupaten Wonosobo*
