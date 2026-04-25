"""
Posyandu AI Agent — Aidi, single unified agent for warga/kader/bidan.
Uses Deepseek for text + function calling, Groq as fallback.
"""

import os
import json
import logging
import httpx
import database as db
import classifier as clf

logger = logging.getLogger("posyandu.agent")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

AIDI_SYSTEM_PROMPT = """Anda adalah "Aidi", asisten kesehatan anak yang ramah dan hangat
untuk Posyandu Patakbanteng, Desa Patakbanteng, Kecamatan Kejajar, Kabupaten Wonosobo,
Jawa Tengah. Anda menangani warga, kader, dan bidan — satu agent untuk semua.

Tugas utama Anda:
1. Menerima pendaftaran anak baru via data yang dikirim
2. Menjawab pertanyaan tentang kesehatan anak, stunting, dan nutrisi
3. Membuat jadwal Posyandu dan mengirim reminder
4. Memberikan edukasi dan penanganan awal untuk kasus gizi buruk/stunting
5. Membantu kader dan bidan melihat data anak dan statistik

Kemampuan Anda (via tools):
- create_schedule: Membuat jadwal Posyandu atau reminder
- list_schedules: Melihat jadwal yang ada
- list_children: Melihat daftar anak terdaftar
- get_child: Melihat detail satu anak
- get_growth_chart: Generate growth chart PNG untuk Telegram
- classify_child: Klasifikasi status gizi BB/TB WHO
- get_stats: Melihat statistik keseluruhan (total anak, risiko, dll)
- list_posyandu: Melihat daftar Posyandu
- register_child: Mendaftarkan anak baru ke sistem

Klasifikasi risiko WHO BB/TB (untuk referensi):
- Normal (green): z-score >= -1 SD
- Risiko (yellow): -3 SD <= z-score < -1 SD
- Buruk (red): z-score < -3 SD → rujuk segera ke Puskesmas

PENTING — Format Respons:
- Jawab dengan teks biasa Bahasa Indonesia yang natural, seperti ngobrol via WhatsApp
- JANGAN pakai markdown formatting (## **bold** dll)
- Emoji boleh secukupnya
- Gunakan bahasa Indonesia baku dan jelas
- Tulis lengkap, pakai titik dan koma dengan benar
- Panggil "Ibu" atau "Bapak" dengan hormat
- Untuk kasus risiko tinggi, sarankan ke Puskesmas/bidan
- Jika Anda menggunakan tool, tunggu hasilnya lalu berikan respons yang jelas
- Untuk pendaftaran anak: ketika warga mengirim data anak, langsung gunakan tool register_child.
  Jika gender (L/P) tidak disebutkan, gunakan default 'L' dan tetap proses.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_schedule",
            "description": "Membuat jadwal Posyandu atau reminder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "scheduled_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "scheduled_time": {"type": "string", "description": "HH:MM"},
                    "target_role": {"type": "string", "enum": ["warga", "kader", "bidan", "semua"]},
                    "reminder_days_before": {"type": "integer"}
                },
                "required": ["title", "scheduled_date", "scheduled_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_schedules",
            "description": "Melihat daftar jadwal yang sudah dibuat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_role": {"type": "string", "enum": ["warga", "kader", "bidan", "semua"]}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_children",
            "description": "Melihat semua anak yang terdaftar di Posyandu."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_child",
            "description": "Melihat detail satu anak berdasarkan NIK.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nik": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_growth_chart",
            "description": "Generate growth chart PNG. Returns chart as base64.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nik": {"type": "string"},
                    "chart_type": {"type": "string", "enum": ["wfa", "hfa"], "default": "wfa"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "classify_child",
            "description": "Klasifikasi status gizi BB/TB menggunakan WHO.",
            "parameters": {
                "type": "object",
                "properties": {
                    "age_months": {"type": "integer"},
                    "gender": {"type": "string", "enum": ["L", "P"]},
                    "weight_kg": {"type": "number"},
                    "height_cm": {"type": "number"}
                },
                "required": ["age_months", "gender", "weight_kg", "height_cm"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stats",
            "description": "Melihat statistik keseluruhan Posyandu."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_posyandu",
            "description": "Melihat daftar Posyandu yang ada."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_child",
            "description": "Mendaftarkan anak baru. Panggil langsung tanpa bertanya lagi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nik": {"type": "string", "description": "16 digit, opsional"},
                    "name": {"type": "string"},
                    "date_of_birth": {"type": "string", "description": "YYYY-MM-DD"},
                    "gender": {"type": "string", "enum": ["L", "P"], "description": "Default 'L' jika tidak tahu"},
                    "parent_name": {"type": "string"},
                    "parent_phone": {"type": "string"},
                    "address": {"type": "string"},
                    "rt_rw": {"type": "string"}
                },
                "required": ["name", "date_of_birth", "gender", "parent_name", "address"]
            }
        }
    },
]


class AidiAgent:
    def __init__(self):
        self.deepseek_key = DEEPSEEK_API_KEY
        self.deepseek_model = DEEPSEEK_MODEL
        self.deepseek_url = DEEPSEEK_BASE_URL
        self.groq_key = GROQ_API_KEY
        self.groq_model = GROQ_MODEL
        self.groq_url = GROQ_BASE_URL

    # ── LLM call with Deepseek primary + Groq fallback ──────────────

    async def _call_llm(self, messages: list, tools: list = None) -> dict:
        payload_base = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512,
        }
        if tools:
            payload_base["tools"] = tools
            payload_base["tool_choice"] = "auto"

        # Try Deepseek first
        try:
            payload = {"model": self.deepseek_model, **payload_base}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.deepseek_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.deepseek_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]
                logger.warning(f"Deepseek error {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Deepseek call failed: {e}, trying Groq")

        # Fallback to Groq
        if not self.groq_key:
            return {"content": "Maaf, layanan AI sedang tidak tersedia. Coba lagi nanti."}
        try:
            payload = {"model": self.groq_model, **payload_base}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.groq_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]
                logger.warning(f"Groq error {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Groq fallback failed: {e}")

        return {"content": "Maaf, layanan AI sedang tidak tersedia. Coba lagi nanti."}

    # ── Tool executors ────────────────────────────────────────────────

    async def _exec_create_schedule(self, args: dict) -> str:
        try:
            sid = await db.add_schedule(args)
            return (f"Jadwal berhasil dibuat! ID: {sid}\n\n"
                    f"Judul: {args['title']}\n"
                    f"Tanggal: {args['scheduled_date']} pukul {args['scheduled_time']}\n"
                    f"Untuk: {args.get('target_role', 'warga')}\n"
                    f"Deskripsi: {args.get('description', '-')}")
        except Exception as e:
            return f"Gagal membuat jadwal: {e}"

    async def _exec_list_schedules(self, args: dict) -> str:
        try:
            rows = await db.get_schedules(target_role=args.get("target_role"))
            if not rows:
                return "Belum ada jadwal. Mau saya buatkan?"
            lines = ["Jadwal Posyandu:"]
            for r in rows:
                lines.append(f"• {r['scheduled_date']} {r['scheduled_time']} — {r['title']} ({r.get('target_role','warga')})")
            return "\n".join(lines)
        except Exception as e:
            return f"Gagal mengambil jadwal: {e}"

    async def _exec_list_children(self, _) -> str:
        try:
            rows = await db.get_all_children()
            if not rows:
                return "Belum ada anak terdaftar."
            lines = [f"Daftar Anak Terdaftar ({len(rows)}):"]
            for r in rows:
                lines.append(f"• {r['name']} ({r['gender']}) — {r['address']} [{r['risk_status']}]")
            return "\n".join(lines)
        except Exception as e:
            return f"Gagal mengambil data anak: {e}"

    async def _exec_get_growth_chart(self, args: dict) -> str:
        try:
            nik = args.get("nik")
            chart_type = args.get("chart_type", "wfa")
            child = await db.get_child_by_nik(nik) if nik else None
            if not child:
                return f"Tidak ditemukan anak dengan NIK {nik}."
            meas = await db.get_child_measurements(child["id"])
            if not meas:
                return f"Belum ada data pengukuran untuk {child['name']}."
            import chart_generator as cg
            png_data = cg.generate_growth_chart_png(
                child["name"], child["gender"], meas, chart_type
            )
            import base64
            b64 = base64.b64encode(png_data).decode()
            return f"[CHART_BASE64]{b64}[/CHART_BASE64]"
        except Exception as e:
            import traceback; traceback.print_exc()
            return f"Gagal membuat growth chart: {e}"

    async def _exec_get_child(self, args: dict) -> str:
        try:
            nik = args.get("nik")
            child = await db.get_child_by_nik(nik) if nik else None
            if not child:
                return f"Tidak ditemukan anak dengan NIK {nik}."
            records = await db.get_health_records(child["id"])
            lines = [
                f"Nama: {child['name']}",
                f"NIK: {child['nik']} | {child['gender']} | {child['date_of_birth']}",
                f"Orang Tua: {child['parent_name']} | Telp: {child['parent_phone']}",
                f"Alamat: {child['address']}",
                f"Status Gizi: {child['risk_status']}",
                f"Riwayat Pengukuran: {len(records)}x",
            ]
            for rec in records[-3:]:
                lines.append(f"  - {rec['date']}: BB={rec['weight_kg']}kg, TB={rec['height_cm']}cm → {rec['bb_tb_status']}")
            return "\n".join(lines)
        except Exception as e:
            return f"Gagal mengambil data anak: {e}"

    async def _exec_classify_child(self, args: dict) -> str:
        try:
            result = clf.classify_bb_tb(
                age_months=args["age_months"],
                gender=args["gender"],
                weight_kg=args["weight_kg"],
                height_cm=args["height_cm"],
            )
            lines = [
                f"Hasil Klasifikasi Gizi:",
                f"Umur: {args['age_months']} bulan | Jenis Kelamin: {args['gender']}",
                f"Berat: {args['weight_kg']}kg | Tinggi: {args['height_cm']}cm",
                f"Z-score: {result.get('z_score', 'N/A')}",
                f"Status: {result['status']} - {result.get('label', '')}",
                f"Saran: {result.get('advice', '')}",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"Gagal klasifikasi: {e}"

    async def _exec_get_stats(self, _) -> str:
        try:
            s = await db.get_statistics()
            lines = [
                f"Statistik Posyandu Patakbanteng:",
                f"Total Anak Terdaftar: {s['total']}",
                f"Normal: {s['green']}",
                f"Risiko: {s['yellow']}",
                f"Rujuk: {s['red']}",
                f"Belum Diukur: {s.get('unmeasured', 0)}",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"Gagal mengambil statistik: {e}"

    async def _exec_list_posyandu(self, _) -> str:
        try:
            rows = await db.get_all_posyandus()
            if not rows:
                return "Belum ada data Posyandu."
            HARI = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
            lines = ["Daftar Posyandu:"]
            for r in rows:
                hari = HARI[r["schedule_day"] - 1] if r["schedule_day"] else "?"
                lines.append(f"• {r['name']} — {r['location']} (hari: {hari})")
            return "\n".join(lines)
        except Exception as e:
            return f"Gagal mengambil data Posyandu: {e}"

    async def _exec_register_child(self, args: dict) -> str:
        try:
            import random
            args.setdefault('nik', f"TEMP{random.randint(10000000, 99999999)}")
            args.setdefault('parent_phone', '-')
            args.setdefault('rt_rw', '-')
            child_id = await db.add_child(args)
            return (f"Berhasil! Anak '{args['name']}' sudah terdaftar.\n"
                    f"NIK: {args['nik']} | ID: {child_id}\n"
                    f"Orang Tua: {args.get('parent_name', '-')}\n"
                    f"Alamat: {args.get('address', '-')}\n\n"
                    f"Data tersimpan di sistem Posyandu Patakbanteng.")
        except Exception as e:
            return f"Gagal mendaftarkan anak: {e}"

    async def _execute_tool(self, name: str, args: dict) -> str:
        executors = {
            "create_schedule": self._exec_create_schedule,
            "list_schedules": self._exec_list_schedules,
            "list_children": self._exec_list_children,
            "get_child": self._exec_get_child,
            "get_growth_chart": self._exec_get_growth_chart,
            "classify_child": self._exec_classify_child,
            "get_stats": self._exec_get_stats,
            "list_posyandu": self._exec_list_posyandu,
            "register_child": self._exec_register_child,
        }
        fn = executors.get(name)
        if fn:
            return await fn(args)
        return f"Tool {name} tidak dikenal."

    # ── Main process ──────────────────────────────────────────────────

    async def process(self, text: str, telegram_id: str) -> str:
        # Load conversation history (last 5 messages)
        try:
            history = await db.get_conversation_history(telegram_id, limit=5)
        except Exception:
            history = []

        msgs = [{"role": "system", "content": AIDI_SYSTEM_PROMPT}]
        for entry in history:
            if entry.get("message") and entry["message"].strip():
                msgs.append({"role": entry.get("role", "user"), "content": entry["message"]})
            if entry.get("response") and entry["response"].strip():
                msgs.append({"role": "assistant", "content": entry["response"]})
        msgs.append({"role": "user", "content": text})

        # First LLM call with tools
        response = self._call_llm(msgs, tools=TOOLS)
        if hasattr(response, '__await__'):
            response = await response

        # Handle function call
        if "tool_calls" in response:
            tool_call = response["tool_calls"][0]
            fn_name = tool_call["function"]["name"]
            fn_args_raw = tool_call["function"]["arguments"]
            fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else (fn_args_raw or {})

            tool_result = await self._execute_tool(fn_name, fn_args)

            # Feed result back to LLM for final response
            msgs.append(response)
            msgs.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result
            })
            final = self._call_llm(msgs)
            if hasattr(final, '__await__'):
                final = await final
            final_content = final.get("content", tool_result)

            try:
                await db.save_conversation(telegram_id, None, "user", text, final_content)
            except Exception:
                pass
            return final_content

        # No tool call — direct response
        content = response.get("content", "Maaf, saya tidak bisa menjawab saat ini.")
        try:
            await db.save_conversation(telegram_id, None, "user", text, content)
        except Exception:
            pass
        return content


# Singleton
_agent = AidiAgent()


async def process_message(text: str, telegram_id: str) -> str:
    return await _agent.process(text, telegram_id)
