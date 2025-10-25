# 🎯 Quick Test - Debug Transcript Block

## ✅ Система работает! 

Блок показывает "Waiting for transcription..." - это нормально!

---

## 🚀 Быстрый тест (30 сек):

### Шаг 1: Откройте UI
```
http://localhost:3001
```

### Шаг 2: Прокрутитесь вниз к "Debug & Input Modes"
Вы должны увидеть:
```
📝 LIVE TRANSCRIPT (LAST 5 LINES):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Waiting for transcription...
```

### Шаг 3: Нажмите на TAB "Text" (вторая вкладка)

### Шаг 4: Вставьте ЛЮБОЙ текст:
```
Halo, nama saya Budi dari CodeSchool.
Bagaimana kabar Anda hari ini?
Saya ingin tahu tentang anak Anda.
Berapa umurnya?
Apakah dia tertarik dengan coding?
```

### Шаг 5: Нажмите "Process Transcript"

**РЕЗУЛЬТАТ:**
Блок обновится и покажет **те же строки** которые вы вставили! ✅

---

## 📊 Что будет видно:

**До (сейчас):**
```
📝 LIVE TRANSCRIPT (LAST 5 LINES):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Waiting for transcription...
```

**После (после Process Transcript):**
```
📝 LIVE TRANSCRIPT (LAST 5 LINES):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Halo, nama saya Budi dari CodeSchool.
Bagaimana kabar Anda hari ini?
Saya ingin tahu tentang anak Anda.
Berapa umurnya?
Apakah dia tertarik dengan coding?
```

---

## 🔍 Если ничего не меняется:

### Проверьте консоль браузера (F12):
```javascript
// Откройте Console
// Должны видеть логи типа:
📨 Получено: {hint: "...", prob: 0.75, transcript_preview: "..."}
```

### Или тестируйте YouTube URL:
1. Перейдите на TAB "YouTube"
2. Вставьте: `https://youtu.be/_YkFL01tJag`
3. Нажмите "Process YouTube"
4. **Блок заполнится текстом из видео!** 🎬

---

## ✨ Как работает внутри:

```
Text Mode:
User pastes text → "Process Transcript" 
  ↓
Backend /api/process-transcript
  ↓
Анализирует текст (LLM, checklist, etc)
  ↓
WebSocket /coach отправляет JSON:
{
  "hint": "...",
  "transcript_preview": "Halo, nama...\nBagaimana..."
}
  ↓
Frontend получает → обновляет блок! ✅
```

---

## 🎬 Live Recording (когда захочешь):

1. "Start Live Recording"
2. Выбери YouTube tab
3. Нажми Share
4. **Блок заполнится в реальном времени!**

---

**Попробуй прямо сейчас! 👆**
