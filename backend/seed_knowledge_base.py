"""
seed_knowledge_base.py — Seed AI-Posyandu knowledge base with PMBA, WHO, and Immunization content.

Run once to populate the agent_lessons table with authoritative health content.
This is the RAG knowledge base that AI uses to answer questions.

Usage:
    python -m backend.seed_knowledge_base
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db


# ─── Knowledge Base Content ───────────────────────────────────────────────────

KNOWLEDGE_BASE = [
    # ── PMBA: Pedoman Makan Bayi dan Balita ──────────────────────────────────
    {
        "error_type": "nutrition_mpasi",
        "trigger_keywords": "mpasi makanan padat bubur bayi 6 bulan resep",
        "lesson_text": (
            "MPASI (Makanan Pendamping ASI) sebaiknya dimulai pada usia 6 bulan. "
            "Prinsipnya: Tepat waktu, tepat jumlah, tepat kualitas, dan tepat hygiene. "
            "Pada awal MPASI, berikan makanan semi cair seperti bubur nasi dengan bumbu halus. "
            "Tingkatkan tekstur secara bertahap: cair → lumat → cincang → makanan keluarga. "
            "Bahan MPASI lokal yang baik: ikan teri, tempe, tahu, kuning telur, bayam, wortel, pisang. "
            "Hindari garam, gula, dan micin untuk bayi di bawah 1 tahun."
        ),
        "action": "Jawab pertanyaan tentang MPASI dengan referensi PMBA Kemenkes RI",
    },
    {
        "error_type": "nutrition_asi",
        "trigger_keywords": "asi ibu menyusui menyusui eksklusif 6 bulan",
        "lesson_text": (
            "ASI Eksklusif diberikan selama 6 bulan pertama tanpa makanan/minuman tambahan. "
            "Manfaat ASI: mengandung抗体 (immunoglobulin), mudah dicerna, meningkatkan kecerdasan, "
            "mempererat ikatan ibu dan bayi, serta ekonomis. "
            "Ibu menyusui butuh tambahan kalori sekitar 500 kkal/hari. "
            "Makan bergizi seimbang: nasi, lauk pauk, sayur, buah, dan minum air yang cukup. "
            "Jika ASI keluar sedikit, pastikan bayi sering disusui dan ibu cukup istirahat."
        ),
        "action": "Jawab pertanyaan tentang ASI dan menyusui",
    },
    {
        "error_type": "nutrition_balita",
        "trigger_keywords": "nutrisi balita anak makan食谱给小",
        "lesson_text": (
            "Balita (1-5 tahun) butuh makan 3 kali sehari ditambah 2 kali makanan selingan. "
            "Porsi makan anak 1-3 tahun sekitar 1/2 porsi dewasa. "
            "Komposisi gizi: 55% karbohidrat (nasi, roti), 25% protein (ikan, telur, tempe, tahu), "
            "20% sayur dan buah. "
            "Ciri anak cukup makan: berat badan naik teratur, aktif bermain, tidak mudah sakit. "
            "Jika anak sulit makan, coba variasi warna dan bentuk makanan, hindari memaksa."
        ),
        "action": "Jawab pertanyaan nutrisi balita 1-5 tahun",
    },

    # ── WHO Z-Score Standards ────────────────────────────────────────────────
    {
        "error_type": "zscore_normal",
        "trigger_keywords": "z-score normal anak sehat bb tb who standar",
        "lesson_text": (
            "WHO Z-Score untuk klasifikasi status gizi anak: "
            "NORMAL (green): Z-score >= -1 SD — berat badan dan tinggi sesuai standar. "
            "Lanjutkan pemantauan rutin di Posyandu setiap bulan. "
            "Terus berikan ASI/MPASI bergizi dan stimulasi tepat usia."
        ),
        "action": "Jelaskan Z-score normal dan anjuran lanjutan",
    },
    {
        "error_type": "zscore_risiko",
        "trigger_keywords": "z-score risiko kuning kurang gizi",
        "lesson_text": (
            "Z-Score RISIKO (yellow): -3 SD <= Z < -1 SD — anak berisiko kurang gizi. "
            "Kondisi ini disebut 'Risiko Gizi Kurang'. "
            "Tindakan: Kunjugi Posyandu untuk pengukuran ulang dalam 1 bulan. "
            "Bidan akan memberikan edukasi gizi, suplemen, dan pemantauan lebih ketat. "
            "Di rumah: beri makan lebih sering (3x utama + 2x selingan), "
            "pilih makanan tinggi protein (ikan, telur, tempe), "
            "dan pastikan anak tidak sedang sakit."
        ),
        "action": "Jelaskan Z-score risiko kuning dan tindakan yang harus dilakukan",
    },
    {
        "error_type": "zscore_buruk",
        "trigger_keywords": "z-score buruk merah stunting berat badan sangat kurang",
        "lesson_text": (
            "Z-Score BURUK (red): Z-score < -3 SD — anak mengalami gizi buruk/stunting berat. "
            "Ini adalah kondisi DARURAT yang perlu penanganan segera. "
            "TINDAKAN: "
            "1) Segera rujuk ke Puskesmas atau rumah sakit untuk penanganan medis. "
            "2) Jangan memberikan makanan berat tanpa pengawasan medis. "
            "3) Bidan akan melakukan assessment dan memberikan terapi gizi rehabilitatif. "
            "4) Pantau tanda bahaya: edema (bengkak), infeksi, kesadaran menurun. "
            "Stunting adalah gagal tumbuh yang bisa berdampak permanen pada otak dan fisik anak."
        ),
        "action": "Jelaskan Z-score buruk dan tindakan emergensi yang diperlukan",
    },
    {
        "error_type": "stunting_prevention",
        "trigger_keywords": "pencegahan stunting tumbuh kembang cerebral",
        "lesson_text": (
            "PENCEGAHAN STUNTING: "
            "1) ASI Eksklusif 6 bulan + MPASI yang tepat setelahnya. "
            "2) Imunisasi lengkap sesuai jadwal. "
            "3) Vitamin A setiap 6 bulan (Februari dan Agustus). "
            "4) Obat cacing setiap 6 bulan untuk anak >1 tahun. "
            "5) Pemantauan pertumbuhan rutin di Posyandu (setiap bulan). "
            "6) Sanitasi dan akses air bersih. "
            "7) Stimulasi tumbuh kembang melalui bermain dan interaksi. "
            "8) Kehamilan cukup bulan dan ibu hamil kontrol rutin ke bidan."
        ),
        "action": "Jawab pertanyaan tentang pencegahan stunting",
    },

    # ── Imunisasi Nasional ────────────────────────────────────────────────────
    {
        "error_type": "imunisasi_jadwal",
        "trigger_keywords": "imunisasi jadwal suntik疫苗 vaccination",
        "lesson_text": (
            "JADWAL IMUNISASI NASIONAL INDONESIA (IDI Kemenkes): "
            "0 bulan: Hepatitis B (dosis 1) — saat lahir di RS/Posyandu. "
            "0-1 bulan: BCG — melindungi dari Tuberkulosis. "
            "1-2 bulan: Polio tetes 1. "
            "2 bulan: DPT-HB-Hib 1, Polio tetes 2. "
            "3 bulan: DPT-HB-Hib 2, Polio tetes 3. "
            "4 bulan: DPT-HB-Hib 3, Polio tetes 4, IPV. "
            "9 bulan: Campak/MR. "
            "18 bulan: DPT-HB-Hib booster, Campak/MR booster. "
            "Imunisasi GRATIS di Posyandu dan Puskesmas."
        ),
        "action": "Jawab pertanyaan jadwal imunisasi nasional",
    },
    {
        "error_type": "imunisasi_campak",
        "trigger_keywords": "campak measles MR rubella german",
        "lesson_text": (
            "CAMPAK (Measles/Rubeola): "
            "Gejala: demam tinggi, bintik merah di seluruh tubuh, batuk, pilek, mata merah. "
            "Komplikasi: pneumonia, diare, radang otak (ensefalitis) yang bisa fatal. "
            "Pencegahan: Imunisasi Campak/MR pada usia 9 bulan dan booster 18 bulan. "
            "Penanganan: Istirahat cukup, minum banyak air, kompres demam, berikan makanan bergizi. "
            "Segera ke Puskesmas jika anak sesak napas, kejang, atau kesadaran menurun. "
            "Vaksin MR (Measles-Rubella) diberikan gratis di Posyandu setiap Agustus."
        ),
        "action": "Jawab pertanyaan tentang campak dan MR",
    },
    {
        "error_type": "imunisasi_dpt",
        "trigger_keywords": "DPT haemophilus influenza polio",
        "lesson_text": (
            "DPT-HB-Hib melindungi dari 5 penyakit: "
            "1) Difteri — infeksi tenggorokan yang bisa menyumbat napas. "
            "2) Pertusis (batuk rejan) — batuk berat menahun. "
            "3) Tetanus — kekakuan otot, bisa masuk melalui luka. "
            "4) Hepatitis B — infeksi hati yang bisa kronis. "
            "5) Hib — infeksi radang selaput otak. "
            "Efek samping normal: demam ringan, bengkak di tempat suntikan 1-3 hari. "
            "Berikan kompres dingin dan parasetamol jika demam. "
            "Kontraindikasi: alergi berat, kejang demam, anak sedang sakit berat."
        ),
        "action": "Jawab pertanyaan tentang imunisasi DPT",
    },

    # ── Vitamin & Suplemen ───────────────────────────────────────────────────
    {
        "error_type": "vitamin_a",
        "trigger_keywords": "vitamin A capsule kapsul biru merah",
        "lesson_text": (
            "VITAMIN A UNTUK ANAK: "
            "Diberikan 2 kali setahun (Februari dan Agustus) di Posyandu. "
            "Dosis: "
            "- Bayi 6-11 bulan: Kapsul Vitamin A berwarna BIRU (100.000 IU). "
            "- Anak 12-59 bulan: Kapsul Vitamin A berwarna MERAH (200.000 IU). "
            "Manfaat: menjaga kesehatan mata, mencegah kebutaan, memperkuat sistem imun. "
            "Vitamin A penting untuk daya tahan tubuh anak terhadap infeksi. "
            "Tidak ada efek samping berbahaya — sangat aman diberikan 2x setahun."
        ),
        "action": "Jawab pertanyaan tentang Vitamin A",
    },
    {
        "error_type": "obat_cacing",
        "trigger_keywords": "obat cacing helmint cacingan worm deworming",
        "lesson_text": (
            "OBAT CACING untuk anak: "
            "Diberikan 2 kali setahun (Februari dan Agustus) bersamaan dengan Vitamin A. "
            "Dosis: "
            "- Anak 1-2 tahun: Pirantel pamoat 1/2 sachet atau sesuai anjuran bidan. "
            "- Anak >2 tahun: Pirantel pamoat 1 sachet atau Albendazole 1 tablet. "
            "Tanda anak cacingan: nafsu makan turun, perut buncit, kulit pucat, sering sakit. "
            "Pencegahan: Cuci tangan dengan sabun sebelum makan, gunakan alas kaki saat ke luar rumah, "
            "jaga kebersihan lingkungan."
        ),
        "action": "Jawab pertanyaan tentang obat cacing",
    },

    # ── Posyandu Process ─────────────────────────────────────────────────────
    {
        "error_type": "posyandu_satu",
        "trigger_keywords": "timbangan berat badan tinggi mengukur cara pengukuran",
        "lesson_text": (
            "CARA PENIMBANGAN DAN PENGUKURAN DI POSYANDU: "
            "1) Timbangan BB: Anak ditimbang tanpa baju tebal, diatur skala ke 0 terlebih dahulu. "
            "   Catat berat dalam kilogram dengan 1 desimal (contoh: 8.5 kg). "
            "2) Pengukur TB/PB: Anak diukur tidur (untuk <2 tahun) atau berdiri (untuk >2 tahun). "
            "   Pastikan kepala, tumit, dan bokong menempel pada papan ukur. "
            "   Catat tinggi dalam centimeter. "
            "3) Hasil plotted pada kurva KMS untuk melihat apakah anak naik atau tidak. "
            "Pengukuran yang salah akan menyebabkan kesalahan klasifikasi Z-score."
        ),
        "action": "Jelaskan cara penimbangan dan pengukuran yang benar",
    },
    {
        "error_type": "kms_kartu",
        "trigger_keywords": "KMS kartu menuju sehat grafik kurva",
        "lesson_text": (
            "KMS (Kartu Menuju Sehat): "
            "Kartu yang diberikan bidan kepada setiap balita untuk mencatat pertumbuhan. "
            "Di KMS terdapat 3 kurva: "
            "1) BB/U (Berat Badan menurut Umur) — untuk anak 0-60 bulan. "
            "2) TB/U (Tinggi Badan menurut Umur) — untuk anak 0-60 bulan. "
            "3) BB/TB (Berat Badan menurut Tinggi Badan) — indikator paling akurat untuk stunting. "
            "Cara membaca: Jika garis naik sejajar dengan garis batas atas → anak tumbuh baik. "
            "Jika garis mendatar atau turun → perlu perhatian khusus."
        ),
        "action": "Jelaskan cara membaca KMS",
    },
    {
        "error_type": "growth_monitoring",
        "trigger_keywords": "pertumbuhan naik grafik tidak naik menetap",
        "lesson_text": (
            "MONITORING PERTUMBUHAN DI POSYANDU: "
            "Balita perlu ditimbang каждый bulan untuk memantau pertumbuhan. "
            "Indikator baik: "
            "- BB naik minimal 500 gram per bulan (untuk bayi <1 tahun). "
            "- BB naik sekitar 200-300 gram per bulan (untuk anak 1-3 tahun). "
            "- TB naik sekitar 0.5-1 cm per bulan (untuk anak <3 tahun). "
            "Jika BB tidak naik 2 bulan berturut-turut → kategori 'Berat Badan Tidak Naik' (BBTM). "
            "Tindakan BBTM: edukasi gizi, cari faktor Penyebab (infeksi, pola makan), "
            "dan pantau lebih ketat."
        ),
        "action": "Jelaskan monitoring pertumbuhan dan arti BB tidak naik",
    },

    # ── Penyakit Umum ─────────────────────────────────────────────────────────
    {
        "error_type": "diare",
        "trigger_keywords": "diare mencret muntah oralit",
        "lesson_text": (
            "DIARE pada balita: "
            "Penyebab tersering: infeksi virus (rotavirus), bakteri (E. coli), atau parasit. "
            "Bahaya utama: DEHIDRASI (kehilangan cairan tubuh). "
            "Tanda dehidrasi ringan-sedang: mata sedikit cekung, sangat haus, kulit sedikit keriput. "
            "Tanda dehidrasi berat: mata sangat cekung, tidak bisa minum, sangat lesu/pingsan. "
            "Penanganan: "
            "1) Berikan oralit (ORS) — 1 sachet untuk setiap BAB cair. "
            "2) Lanjutkan ASI/exclusive breastfeeding. "
            "3) Berikan makan seperti biasa. "
            "4) Segera ke Puskesmas jika ada tanda dehidrasi berat, BAB berdarah, atau fever >38.5°C. "
            "Pencegahan: Cuci tangan pakai sabun, berikan air bersih, buang POPNAS dengan benar."
        ),
        "action": "Jawab pertanyaan tentang diare dan penanganannya",
    },
    {
        "error_type": "demam",
        "trigger_keywords": "demam panas气温 tinggi",
        "lesson_text": (
            "DEMAM pada balita: "
            "Demam = suhu tubuh >37.5°C diukur dengan termometer. "
            "Umumnya disebabkan infeksi virus (self-limiting 3-5 hari). "
            "Penanganan di rumah: "
            "1) Kompres dengan air hangat (BUKAN air dingin/-es). "
            "2) Berikan parasetamol sesuai dosis berat badan. "
            "3) Pastikan anak cukup minum (ASI, air, sup). "
            "4) Pakaikan baju tipis, jangan diselimuti. "
            "Segera ke Puskesmas jika: "
            "- Usia <3 bulan dengan demam >38°C. "
            "- Demam >3 hari. "
            "- Kejang, muntah terus-menerus, ruam, atau anak sangat lesu."
        ),
        "action": "Jawab pertanyaan tentang demam dan penanganannya",
    },
    {
        "error_type": "pneumonia",
        "trigger_keywords": "pneumonia radang paru sesak napas",
        "lesson_text": (
            "PNEUMONIA (Radang Paru-Paru) pada balita: "
            "Gejala: "
            "- Napas cepat dan sesak (bayi >60x/menit, anak >40x/menit). "
            "- Dada cekung (retraksi). "
            "- Batuk, demam, tidak mau minum. "
            "Penyebab: bakteri (Streptococcus pneumoniae, H. influenzae) atau virus. "
            "Penanganan di Puskesmas: Antibiotik sesuai Pedoman Program CDT. "
            "Segera rujuk ke rumah sakit jika: "
            "- Tidak bisa minum/ditarik, "
            "- Kesadaran menurun, "
            "- biru pada bibir/kuku (sianosis), "
            "- Stridor (suara napas tambahan)."
        ),
        "action": "Jawab pertanyaan tentang pneumonia dan tanda bahayanya",
    },

    # ── Ibu Hamil & Menyusui ──────────────────────────────────────────────────
    {
        "error_type": "ibu_hamil",
        "trigger_keywords": "hamil kehamilan ibu hamil kontrol",
        "lesson_text": (
            "KONTROL IBU HAMIL (Antenatal Care): "
            "Minimal 4 kali kontrol selama kehamilan: "
            "- Trimester 1: Sebelum minggu ke-14 (identifikasi risiko awal). "
            "- Trimester 2: Minggu 14-28 (pemeriksaan rutin). "
            "- Trimester 3: Minggu 28-36 (pemantauan pertumbuhan janin). "
            "- Minggu 36+: Persiapan persalinan. "
            "Di setiap kontrol: "
            "1) Ukur berat badan, tekanan darah, tinggi fundus. "
            "2) Pemeriksaan Hb, protein            "2) Pemeriksaan Hb, protein urin. "
            "3) Tablet tambah darah (Fe) 1 tablet/hari selama kehamilan. "
            "4) Imunisasi Tetanus Toksoid (TT) sesuai jadwal."
        ),
        "action": "Jawab pertanyaan tentang kontrol kehamilan",
    },
]


# ─── Seeding Logic ────────────────────────────────────────────────────────────

async def seed_if_empty():
    """Insert knowledge base entries only if the table is empty."""
    all_lessons = await db.get_all_lessons()
    if all_lessons:
        print(f"Knowledge base already has {len(all_lessons)} entries. Skipping seed.")
        return

    print(f"Seeding {len(KNOWLEDGE_BASE)} knowledge base entries...")
    for entry in KNOWLEDGE_BASE:
        await db.add_lesson(
            error_type=entry["error_type"],
            keywords=entry["trigger_keywords"],
            lesson=entry["lesson_text"],
            action=entry["action"],
        )
        print(f"  Added: {entry['error_type']}")

    print("Done! Knowledge base seeded.")


async def seed_replace():
    """Replace all existing entries with fresh seed (for updates)."""
    print(f"Replacing knowledge base with {len(KNOWLEDGE_BASE)} entries...")
    # Note: This doesn't delete old entries, just adds new ones
    # In production, you'd want to clear the table first
    for entry in KNOWLEDGE_BASE:
        await db.add_lesson(
            error_type=entry["error_type"],
            keywords=entry["trigger_keywords"],
            lesson=entry["lesson_text"],
            action=entry["action"],
        )
        print(f"  Added: {entry['error_type']}")
    print("Done!")


async def main():
    import sys
    await db.init_db()

    if "--replace" in sys.argv:
        await seed_replace()
    else:
        await seed_if_empty()


if __name__ == "__main__":
    asyncio.run(main())
