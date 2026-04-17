# Patyandu AI

AI-agent-powered platform for stunting prevention and Posyandu activation in Patakbanteng Village, Wonosobo, Jawa Tengah.

## Architecture

- **Telegram Bot** (`bot/`) — warga registration, AI chat, reminders via GPT-5.1
- **FastAPI Backend** (`backend/`) — REST API, SQLite DB, WHO BB/TB classifier, AI agent
- **React Dashboard** (`dashboard/`) — Kader, Bidan, and Kepala Desa views

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
# API running at http://localhost:5001
```

### Telegram Bot
```bash
cd bot
pip install -r requirements.txt
# Add BOT_TOKEN to .env
python main.py
```

### Dashboard
```bash
cd dashboard
npm install
npm run dev
# Open http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/children` | List all children |
| GET | `/api/children/{id}` | Child detail + health records |
| POST | `/api/children` | Register new child |
| POST | `/api/children/{id}/health-record` | Add health record (auto-classifies BB/TB) |
| POST | `/api/agent/chat` | AI Agent chat |
| GET | `/api/agent/classify` | Standalone BB/TB classification |

## WHO BB/TB Classification

- 🟢 **Hijau (Normal)**: >= -1 SD
- 🟡 **Kuning (Risiko)**: -3 SD to < -1 SD → home visit within 7 days
- 🔴 **Merah (Berat)**: < -3 SD → immediate referral to Puskesmas
