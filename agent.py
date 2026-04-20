"""
Patyandu AI Agent — Aidi, single unified agent for warga/kader/bidan.
GPT-5.1 via SumoPod with conversation memory and function-calling tools.
"""

import os
import requests
import json
import database as db
import classifier as clf

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-CJSIoKjjsr-v0NlC7P3IhQ")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://ai.sumopod.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "glm-5")

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
- get_growth_chart: Generate growth chart PNG for Telegram display
- classify_child: Klasifikasi status gizi BB/TB WHO
- get_stats: Melihat statistik keseluruhan (total anak, risiko, dll)
- list_posyandu: Melihat daftar Posyandu
- register_child: Mendaftarkan anak baru ke sistem

Klasifikasi risiko WHO BB/TB (untuk referensi):
- Normal (green): z-score >= -1 SD
- Risiko (yellow): -3 SD <= z-score < -1 SD → kunjungan rumah 7 hari
- Buruk (red): z-score < -3 SD → rujuk segera ke Puskesmas

PENTING — Format Respons:
- Jawab dengan teks biasa Indonesia yang natural, seperti mengobrol via WhatsApp
- JANGAN pakai markdown formatting seperti ## heading, **bold**, ### subheading
- Emoji boleh digunakan secukupnya untuk暄ans/prasaran
- Gunakan bahasa Indonesia yang baku dan jelas
- Jangan gunakan singkatan seperti 'n' untuk 'dan', 'de' untuk 'dengan', atau slang lainnya
- Tulis lengkap dan rapi, gunakan titik dan koma dengan benar
- Tulis seperti pesanchat biasa: paragraf, nomor sederhana seperti 1. 2. 3.
- Panggil "Ibu" atau "Bapak" dengan hormat sesuai konteks
- Untuk kasus risiko tinggi, sarankan ke Puskesmas/bidan
- Jika Anda menggunakan tool, tunggu hasilnya lalu berikan respons yang jelas
- Tool adalah kekuatan Anda — gunakan dengan percaya diri untuk membantu
- Untuk pendaftaran anak: ketika warga mengirim nama anak, tanggal lahir, nama orang tua, alamat, dan NIK, langsung gunakan tool register_child untuk menyimpan ke sistem. Jika gender (L/P) tidak disebutkan, gunakan default 'L' (laki-laki) dan tetap proses tanpa bertanya.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_schedule",
            "description": "Membuat jadwal Posyandu atau reminder. Gunakan ini ketika pengguna ingin membuat jadwal kegiatan, Posyandu, atau mengingatkan warga.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Judul jadwal, contoh: 'Posyandu Bulanan'"},
                    "description": {"type": "string", "description": "Deskripsi kegiatan"},
                    "scheduled_date": {"type": "string", "description": "Tanggal jadwal (format: YYYY-MM-DD)"},
                    "scheduled_time": {"type": "string", "description": "Waktu jadwal (format: HH:MM)"},
                    "target_role": {"type": "string", "enum": ["warga", "kader", "bidan", "semua"], "description": "Siapa yang dituju"},
                    "reminder_days_before": {"type": "integer", "description": "Berapa hari sebelum untuk reminder"}
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
            "description": "Melihat detail satu anak berdasarkan NIK atau ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nik": {"type": "string", "description": "NIK anak"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_growth_chart",
            "description": "Generate growth chart PNG for Telegram. Returns chart as base64 PNG.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nik": {"type": "string", "description": "NIK of the child"},
                    "chart_type": {"type": "string", "enum": ["wfa", "hfa"], "default": "wfa"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "classify_child",
            "description": "Klasifikasi status gizi BB/TB anak menggunakan WHO.",
            "parameters": {
                "type": "object",
                "properties": {
                    "age_months": {"type": "integer", "description": "Umur anak dalam bulan"},
                    "gender": {"type": "string", "enum": ["L", "P"], "description": "Jenis kelamin: L=laki, P=perempuan"},
                    "weight_kg": {"type": "number", "description": "Berat anak dalam kg"},
                    "height_cm": {"type": "number", "description": "Tinggi anak dalam cm"}
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
            "description": "Mendaftarkan anak baru ke sistem Posyandu. Gunakan ketika warga mengirim data pendaftaran anak (nama, tanggal lahir, nama orang tua, alamat, NIK). Langsung panggil tool ini tanpa perlu bertanya lagi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nik": {"type": "string", "description": "NIK anak (16 digit). Opsional jika belum punya."},
                    "name": {"type": "string", "description": "Nama lengkap anak"},
                    "date_of_birth": {"type": "string", "description": "Tanggal lahir (format: YYYY-MM-DD)"},
                    "gender": {"type": "string", "enum": ["L", "P"], "description": "Jenis kelamin: L=laki-laki, P=perempuan. Jika tidak tahu, isi 'L' sebagai default."},
                    "parent_name": {"type": "string", "description": "Nama orang tua/wali"},
                    "parent_phone": {"type": "string", "description": "Nomor telepon orang tua"},
                    "address": {"type": "string", "description": "Alamat lengkap"},
                    "rt_rw": {"type": "string", "description": "RT/RW (format: RT01/RW02)"}
                },
                "required": ["name", "date_of_birth", "gender", "parent_name", "address"]
            }
        }
    },
]


class AidiAgent:
    def __init__(self, model: str = MODEL_NAME):
        self.model = model
        self.api_key = OPENAI_API_KEY
        self.base_url = OPENAI_BASE_URL
        # Reuse session for connection pooling — faster & less memory churn
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3
        )
        self.session.mount("https://", adapter)

    # ── LLM with function calling ─────────────────────────────────────────

    def _call_llm(self, messages: list, tools: list = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512,
        }
        if tools:
            payload["tools"] = tools

        try:
            resp = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if resp.status_code != 200:
                return {"content": "Maaf, saya sedang tidak bisa menjawab. Coba lagi nanti."}
            return resp.json()["choices"][0]["message"]
        except requests.exceptions.Timeout:
            return {"content": "Maaf, koneksi lambat. Coba lagi sesaat."}
        except Exception:
            return {"content": "Maaf, terjadi kesalahan teknis. Coba lagi nanti."}

    # ── Tool executors ────────────────────────────────────────────────────

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
            # Fill defaults for missing required fields
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

    # ── Main process ─────────────────────────────────────────────────────────

    async def process(self, text: str, telegram_id: str) -> str:
        # Load conversation history
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

        # Handle function call
        if "tool_calls" in response:
            tool_call = response["tool_calls"][0]
            fn_name = tool_call["function"]["name"]
            fn_args_raw = tool_call["function"]["arguments"]; fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else (fn_args_raw or {})

            tool_result = await self._execute_tool(fn_name, fn_args)

            # Feed result back to LLM for final response
            msgs.append(response)
            msgs.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result
            })
            final = self._call_llm(msgs)
            final_content = final.get("content", tool_result)

            # Save
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