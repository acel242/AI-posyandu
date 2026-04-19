# PRD-003: Growth Chart Visualization

## 1. Concept & Vision

Fitur visualisasi grafik pertumbuhan anak (Growth Chart / Growth Curve) berdasarkan data WHO BB/U, BB/TB, dan TB/U. Grafik ini menggantikan KMS fisik dan memungkinkan kader, bidan, dan orang tua melihat secara langsung trajectory pertumbuhan anak dibanding standar WHO.

Tampilan: Clean, mobile-friendly, bisa dilihat langsung di Telegram chat (via inline chart) atau di dashboard web.

## 2. Problem It Solves

- KMS fisik mudah hilang,写得乱七八糟
- Kader harus gambar manual di buku KMS — sering salah
- Orang tua tidak punya visibility growth anak
- Tidak ada historical view yang mudah

## 3. User Stories

### Sebagai ORANG TUA (Warga)
- Saya mau lihat grafik pertumbuhan anak saya dalam 6 bulan terakhir
- Saya mau tahu apakah anak saya masuk zona hijau, kuning, atau merah
- Saya mau bisa share grafik ke bidan/kader

### Sebagai KADER
- Saya mau input berat & tinggi anak langsung dari chat (tanpa buka dashboard)
- Saya mau lihat growth chart seluruh balita di desa saya
- Saya mau dapat alert kalau ada anak masuk zona merah

###Sebagai BIDAN
- Saya mau lihat daftar anak dengan growth tidak optimal
- Saya mau bandingkan growth antar anak
- Saya mau export data untuk laporan ke Puskesmas

## 4. Technical Approach

### Data Model
```
Child:
  - id, name, date_of_birth, gender
  - parent_name, parent_phone

Measurement:
  - id, child_id, date, weight_kg, height_cm
  - classification (green/yellow/red based on WHO)
  - z_score_bb_u, z_score_bb_tb, z_score_tb_u
```

### WHO Standards
- Gunakan WHO Anthro Calculator library (Python) untuk hitung z-scores
- WHO Growth Reference 2007 untuk anak 0-5 tahun
- Klasifikasi:
  - Hijau (Normal): z-score >= -1 SD
  - Kuning (Risiko): -2 SD <= z-score < -1 SD  
  - Merah (Stunting/Gizi Buruk): z-score < -2 SD

### Visualization Options

#### Option A: Inline Chart di Telegram
- Generate PNG via matplotlib/plotly
- Send as photo via Telegram Bot API
- Simpel, no frontend needed

#### Option B: Interactive Chart di Dashboard
- Recharts (React) untuk dashboard
- Line chart dengan WHO percentile bands
- Hover untuk lihat detail tiap point

#### Option C: Hybrid (Option A + B)
- Chat command → inline PNG ke Telegram
- Full dashboard untuk kader/bidan

**Decision: Option C (Hybrid)**

### API Endpoints
```
GET  /api/children/{id}/measurements
     → Returns list of measurements with z-scores

GET  /api/children/{id}/growth-chart.png
     → Returns generated chart as image

GET  /api/children/{id}/growth-data
     → Returns JSON for frontend charting

POST /api/measurements
     → Add new measurement (auto-classify)
```

### Tool untuk Agent Aidi
```python
get_child_growth_chart(child_id: int) -> Image/URL
get_child_growth_history(child_id: int) -> List[Measurement]
```

## 5. UI/UX Design

### Telegram Response (Orang Tua)
```
📊 Grafik Pertumbuhan: Kevin (3 tahun)

[GROWTH CHART IMAGE - PNG]

📅 6 Bulan Terakhir:
• Berat: 12kg → 14kg ✅ Naik
• Tinggi: 88cm → 94cm ✅ Naik
• Status: 🟢 Normal (Z-score: -0.5)

💡 Saran: Pertumbuhan baik. Lanjut berikan MPASI bergizi.
```

### Dashboard View (Kader/Bidan)
- Halaman list anak dengan filter: semua, risiko tinggi, stunting
- Klik anak → page detail dengan:
  - Growth chart interaktif (Recharts)
  - Tabel history pengukuran
  - Tombol export PDF
  - Alert card jika zona merah

### Growth Chart Design
- X-axis: Umur (bulan)
- Y-axis: Berat (kg) atau Tinggi (cm)
- Garis pertumbuhan anak (solid line)
- WHO percentile bands:
  - Hijau: Median (garis tengah)
  - Hijau: +1 SD, -1 SD (batas normal)
  - Kuning: -2 SD (batas risiko)
  - Merah: -3 SD (stunting berat)

## 6. Implementation Plan

### Phase 1: Core Backend (1-2 hari)
- [ ] Add `measurements` table to SQLite
- [ ] Implement WHO z-score calculation (python-gzip)
- [ ] GET /api/children/{id}/measurements endpoint
- [ ] POST /api/measurements endpoint with auto-classification

### Phase 2: Chart Generation (1 hari)
- [ ] Install matplotlib or plotly
- [ ] Generate growth chart PNG with WHO reference lines
- [ ] GET /api/children/{id}/growth-chart.png endpoint

### Phase 3: Telegram Integration (1 hari)
- [ ] Add `get_child_growth_chart` tool to agent.py
- [ ] Add `get_child_growth_history` tool to agent.py
- [ ] Update agent prompt untuk aware growth context

### Phase 4: Dashboard (2 hari)
- [ ] Create growth chart page in React
- [ ] Implement Recharts line chart with WHO bands
- [ ] Add measurement history table
- [ ] Export PDF button

### Phase 5: Alerts & Notifications (1 hari)
- [ ] Cron job untuk cek anak zona merah
- [ ] Auto-notify kader via Telegram
- [ ] Dashboard alert banner

## 7. Dependencies

```
Python:
- whois-anto (WHO anthro calculator)
- matplotlib atau plotly (chart generation)
- PIL (image processing)

Frontend:
- recharts (React chart library)
- tailwindcss

Existing:
- FastAPI backend (already exists)
- SQLite database (already exists)
- Telegram bot (already exists)
```

## 8. Priority

**High** — Growth chart adalah core value proposition aplikasi ini. Tanpa ini, aplikasi hanya database pengukuran. Dengan ini, aplikasi jadi alat monitoring yang berguna.

## 9. Out of Scope (for now)

- Login/authentication per role
- PDF export (Phase 4 deferred)
- SMS/WhatsApp notification
- Mobile app (native)
