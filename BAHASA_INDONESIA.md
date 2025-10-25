# 🇮🇩 Bahasa Indonesia Support Guide

## Overview

Sistem sekarang **fully support Bahasa Indonesia** untuk:
- ✅ Transcription (Whisper)
- ✅ Keyword detection untuk checklist
- ✅ Stage detection (Greeting → Discovery → Presentation → Objections → Closing)
- ✅ Client insights (objections, interests, needs)

---

## 🎯 Automatic Checklist Detection (Bahasa)

Sistem secara otomatis mencentang poin-poin checklist berdasarkan kata kunci yang terdeteksi:

### **1. Greeting & Rapport** 👋

| Poin | Kata Kunci Bahasa |
|------|-------------------|
| Perkenalan | "nama saya", "perkenalkan", "saya dari", "dari perusahaan" |
| Cek waktu | "apakah ada waktu", "ada waktu", "bisa bicara", "bisa ngobrol" |
| Set agenda | "hari ini kita akan", "saya ingin", "agendanya", "rencananya" |
| Build rapport | "apa kabar", "bagaimana kabarnya", "gimana kabarnya" |

**Contoh:**
```
"Halo, nama saya Budi dari CodeSchool. Apakah ada waktu 15 menit?"
→ ✓ Introduce yourself
→ ✓ Check if they have time
```

---

### **2. Discovery & Profiling** 🔍

| Poin | Kata Kunci Bahasa |
|------|-------------------|
| Situasi saat ini | "saat ini", "sekarang", "kondisi sekarang" |
| Pain points | "tantangan", "masalah", "kesulitan", "kendala", "hambatan" |
| Goals | "tujuan", "ingin", "mau", "harapan", "berharap", "mencapai" |
| Decision process | "siapa lagi", "keputusan", "persetujuan", "yang terlibat" |
| Budget/timeline | "anggaran", "biaya", "harga", "kapan", "waktu" |
| Stakeholders | "tim", "siapa lagi", "yang lain", "terlibat" |

**Contoh:**
```
"Anak saya saat ini berumur 10 tahun. Saya ingin dia bisa berpikir logis."
→ ✓ Understand current situation
→ ✓ Discover goals
```

---

### **3. Solution Presentation** 📊

| Poin | Kata Kunci Bahasa |
|------|-------------------|
| Tailor solution | "berdasarkan yang anda bilang", "khusus untuk", "sesuai kebutuhan" |
| Demo features | "saya tunjukkan", "fitur", "bisa", "memungkinkan" |
| Show value | "hemat", "manfaat", "nilai", "keuntungan", "hasil" |
| Examples | "contoh", "studi kasus", "klien lain", "pelanggan" |
| Check understanding | "jelas", "paham", "mengerti", "ada pertanyaan" |

**Contoh:**
```
"Berdasarkan yang Anda bilang tadi, saya tunjukkan fitur yang cocok."
→ ✓ Tailor solution to their needs
→ ✓ Demo key features
```

---

### **4. Objection Handling** 💬

| Poin | Kata Kunci Bahasa |
|------|-------------------|
| Price concerns | "harga", "biaya", "mahal", "terlalu mahal", "investasi" |
| Time concerns | "waktu", "implementasi", "tidak ada waktu", "sibuk" |
| Competition | "bandingkan", "dibanding", "beda", "alternatif", "kompetitor" |
| Risks | "risiko", "khawatir", "jaminan", "garansi", "dukungan" |
| Confirm resolution | "selesai", "jelas", "nyaman", "puas", "oke" |

**Contoh:**
```
"Berapa harganya? Wah, terlalu mahal untuk kami."
→ ✓ Address price concerns (ketika Anda merespon)
```

---

### **5. Closing & Next Steps** 🤝

| Poin | Kata Kunci Bahasa |
|------|-------------------|
| Summary | "kesimpulan", "rangkuman", "jadi", "intinya" |
| Ask commitment | "siap untuk", "apakah mau", "bagaimana", "langkah selanjutnya" |
| Schedule followup | "tindak lanjut", "pertemuan selanjutnya", "jadwal", "kalender" |
| Send materials | "kirim", "email", "materi", "proposal", "dokumen" |
| Thank them | "terima kasih", "makasih", "senang", "berterima kasih" |

**Contoh:**
```
"Jadi kesimpulannya, apakah Bapak siap untuk mulai? Saya kirim proposal ya."
→ ✓ Summarize
→ ✓ Ask for commitment
→ ✓ Send materials
```

---

## 📊 Stage Detection (Bahasa)

Sistem otomatis mendeteksi tahap percakapan:

### **Greeting** 👋
**Kata kunci:** halo, hai, selamat pagi/siang, perkenalkan, nama saya

**Active badge muncul saat:**
```
"Halo, selamat siang. Perkenalkan nama saya Budi..."
```

### **Discovery** 🔍
**Kata kunci:** ceritakan, apa yang, tantangan, tujuan, kebutuhan, masalah

**Active badge muncul saat:**
```
"Ceritakan, apa tantangan terbesar Anda saat ini?"
```

### **Presentation** 📊
**Kata kunci:** saya tunjukkan, fitur ini, platform kami, contohnya

**Active badge muncul saat:**
```
"Saya tunjukkan fitur yang sesuai kebutuhan Anda..."
```

### **Objections** 💬
**Kata kunci:** terlalu mahal, tidak ada waktu, khawatir, tapi, namun

**Active badge muncul saat:**
```
"Terlalu mahal untuk kami. Tidak yakin bisa cocok."
```

### **Closing** 🤝
**Kata kunci:** langkah selanjutnya, lanjut, terima kasih, tindak lanjut

**Active badge muncul saat:**
```
"Oke, langkah selanjutnya bagaimana? Kapan bisa mulai?"
```

---

## 🧪 Test Scenarios (Bahasa Indonesia)

### **Test 1: Full Discovery Flow**

**Input:**
```
Halo, nama saya Andi dari TechEdu. Apakah ada waktu 15 menit?
Baik, terima kasih. Hari ini saya ingin mengenal kebutuhan Anda.
Ceritakan, anak Bapak berapa tahun sekarang?
Apa tantangan terbesar yang Bapak hadapi?
Apa tujuan Bapak untuk anak?
```

**Expected Result:**
- Stage: `discovery` (Active)
- Checklist:
  - ✓ Introduce yourself
  - ✓ Check time availability
  - ✓ Set agenda
  - ✓ Understand current situation
  - ✓ Identify pain points
  - ✓ Discover goals

---

### **Test 2: Objection Handling**

**Input:**
```
Client: "Berapa harganya?"
Manager: "Harga kami Rp 500 ribu per bulan."
Client: "Wah, terlalu mahal untuk kami. Tidak mampu."
Manager: "Saya paham kekhawatiran Bapak. Mari saya jelaskan manfaatnya..."
```

**Expected Result:**
- Stage: `objections` (Active)
- Client Insights:
  - Objections: ["price"]
- Checklist:
  - ✓ Address price concerns (setelah manager merespon)

---

### **Test 3: Closing**

**Input:**
```
Jadi kesimpulannya, program kami cocok untuk kebutuhan Bapak.
Apakah Bapak siap untuk mulai trial minggu depan?
Baik, saya jadwalkan pertemuan follow up hari Senin.
Saya kirim proposal dan materi ke email ya.
Terima kasih banyak untuk waktunya.
```

**Expected Result:**
- Stage: `closing` (Active)
- Checklist:
  - ✓ Summarize key benefits
  - ✓ Ask for commitment
  - ✓ Schedule follow-up
  - ✓ Send materials
  - ✓ Thank them

---

## 🎯 Client Insights (Bahasa)

### **Objections Detection:**

| Objection Type | Kata Kunci Bahasa |
|----------------|-------------------|
| Price | "terlalu mahal", "mahal", "tidak mampu", "biaya tinggi" |
| Time | "tidak ada waktu", "sibuk", "terlalu lama" |
| Competition | "sudah pakai yang lain", "kompetitor lebih baik" |

**Contoh:**
```
"Terlalu mahal untuk kami, dan tidak ada waktu untuk implementasi."
→ Objections: ["price", "time"]
```

### **Interests Detection:**

| Interest | Kata Kunci Bahasa |
|----------|-------------------|
| General | "menarik", "bagus", "suka", "keren" |
| Specific | "Minecraft", "coding", "game" (proper nouns tetap sama) |

**Contoh:**
```
"Wah menarik sekali! Anak saya suka Minecraft."
→ Interests: ["Minecraft"]
→ Emotion: "curious" / "engaged"
```

### **Needs Detection:**

**Pola:** "saya ingin [X]", "tujuan saya [X]", "butuh [X]"

**Contoh:**
```
"Saya ingin anak saya bisa berpikir logis."
→ Need: "berpikir logis"
```

---

## 💡 Tips for Better Detection

### **1. Gunakan Frasa Lengkap**
✅ BAIK: "Berdasarkan yang Anda bilang, saya tunjukkan fitur ini"
❌ KURANG: "Ini fitur"

### **2. Jelas dalam Menyebut Pain Points**
✅ BAIK: "Apa tantangan terbesar yang Bapak hadapi?"
❌ KURANG: "Ada masalah?"

### **3. Eksplisit dalam Closing**
✅ BAIK: "Jadi kesimpulannya, langkah selanjutnya bagaimana?"
❌ KURANG: "Gimana?"

---

## 🔧 Custom Keywords

Untuk menambah kata kunci custom, edit `/backend/sales_checklist.py`:

```python
# Contoh: Tambah kata kunci untuk "introduce yourself"
'intro_yourself': [
    'my name is', 'i\'m', 'calling from',  # English
    'nama saya', 'perkenalkan', 'saya dari',  # Bahasa
    'aku namanya', 'gue dari'  # Informal ← TAMBAH DI SINI
],
```

---

## 📱 Quick Reference Card

### **Checklist Auto-Complete Phrases:**

**Greeting:**
- "Nama saya [X] dari [company]"
- "Apakah ada waktu [Y] menit?"
- "Hari ini kita akan..."

**Discovery:**
- "Ceritakan tentang [situasi]"
- "Apa tantangan terbesar?"
- "Apa tujuan Anda?"

**Presentation:**
- "Saya tunjukkan fitur [X]"
- "Berdasarkan kebutuhan Anda..."
- "Contohnya, klien kami..."

**Objections:**
- "Saya paham kekhawatiran Anda"
- "Mari saya jelaskan [value]"
- "Ini berbeda dari kompetitor karena..."

**Closing:**
- "Jadi kesimpulannya..."
- "Apakah siap untuk [next step]?"
- "Saya jadwalkan follow up"
- "Terima kasih untuk waktunya"

---

## 🎓 Best Practices

1. **Speak Naturally** - Sistem mendeteksi frasa natural, bukan kata tunggal
2. **Be Specific** - "Apa tantangan terbesar?" lebih baik dari "Ada masalah?"
3. **Follow Structure** - Ikuti flow: Greeting → Discovery → Presentation → Objections → Closing
4. **Acknowledge Objections** - Sistem hanya centang setelah Anda merespon
5. **Close Properly** - Gunakan kata penutup yang jelas

---

## 🚀 Ready to Test!

Coba dengan test scenario di atas dan lihat checklist otomatis tercentang! 🎯

**Bahasa Indonesia support is LIVE!** 🇮🇩

