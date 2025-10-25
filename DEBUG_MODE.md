# 🔧 Debug Mode - Тестирование без live записи

## Обзор

Debug Mode позволяет тестировать систему анализа без необходимости делать реальные звонки в Google Meet. Вы можете использовать различные источники данных для отладки.

## 🎯 Доступные режимы

### 1. 🎤 Live Recording (текущий)
- Захват аудио в реальном времени из Google Meet
- Требует разрешения на захват экрана
- Работает как раньше

### 2. 📝 Paste Transcript ⭐ **Самый простой!**
- Вставьте текст диалога напрямую
- Мгновенный анализ без записи
- Идеально для быстрой отладки

**Формат текста:**
```
Client: My child is 10 years old and loves Minecraft
Manager: Have you done coding before?
Client: No, but it sounds fun and interesting for future
Manager: What are your goals?
Client: I want him to think logically. How much does it cost?
Manager: Our program starts at $299...
```

**Или без меток (любой текст):**
```
My child is 10 years old and loves Minecraft.
It sounds fun and interesting for future.
I want him to think logically.
How much does it cost?
```

### 3. 🎬 Upload Video File 
- Загрузите видео со звонка
- Поддерживаемые форматы: MP4, MOV, AVI, WebM, MP3, WAV
- ⚠️ **Статус:** Требует установки FFmpeg и faster-whisper (пока не реализовано)

### 4. 📺 YouTube URL
- Вставьте ссылку на YouTube видео со звонком
- Автоматическое скачивание и извлечение аудио
- ⚠️ **Статус:** Требует установки yt-dlp и faster-whisper (пока не реализовано)

---

## 🚀 Как использовать

### Режим 1: Live Recording

1. Выберите таб **"🎤 Live"**
2. Нажмите кнопку **"Начать запись"** ниже
3. Выберите вкладку Google Meet
4. Не забудьте включить "Share audio"!

### Режим 2: Paste Transcript (готов к использованию!)

1. Выберите таб **"📝 Text"**
2. Вставьте текст диалога в поле
3. Нажмите **"✅ Анализировать текст"**
4. Через 1-2 секунды увидите результаты:
   - **Client Insights** (левая панель) обновятся
   - **Sales Coach** (правая панель) покажет подсказки

**Пример текста для тестирования:**
```
Client: My child is 10 years old and loves Minecraft
Client: No, but it sounds fun and interesting for future
Client: I want him to think logically and be more creative
Client: How much does it cost? We're on a budget
Client: That's too expensive for us
```

### Режим 3: Upload Video

1. Выберите таб **"🎬 Video"**
2. Нажмите на зону загрузки или перетащите файл
3. Нажмите **"✅ Загрузить и обработать"**
4. ⚠️ Пока недоступно — вернётся сообщение об ошибке

### Режим 4: YouTube

1. Выберите таб **"📺 YouTube"**
2. Вставьте ссылку (например: `https://www.youtube.com/watch?v=...`)
3. Нажмите **"✅ Загрузить с YouTube"**
4. ⚠️ Пока недоступно — вернётся сообщение об ошибке

---

## 📊 Что анализируется

После обработки любого источника вы увидите:

### Client Insights (левая панель):
- 🧭 **Stage** - этап диалога (Profiling / Presentation / Objection / Closing)
- ❤️ **Emotion** - эмоциональный тон (Engaged / Curious / Hesitant / Defensive / Negative)
- 💬 **Objections** - активные возражения ([price], [time], [family], и т.д.)
- 🌟 **Interests** - интересы клиента ([game-based learning], [logic], и т.д.)
- 📘 **Need** - выявленная потребность ("think logically", "learn programming", и т.д.)
- 📈 **Engagement** - уровень вовлечённости (0-100%) с трендом (↑ ↓ →)

### Sales Coach (правая панель):
- 💡 **Hint** - подсказка от AI (через Claude)
- 📊 **Probability** - вероятность успешной сделки (0-100%)

---

## 🧪 Примеры для тестирования

### Тест 1: Определение возражения по цене
```
Client: My child is 10 and loves games
Client: This sounds great but how much does it cost?
Client: That's too expensive for us, we're on a tight budget
```

**Ожидаемый результат:**
- active_objections: `["price"]`
- emotion: `"hesitant"` или `"defensive"`
- stage: `"objection"`

### Тест 2: Определение интересов
```
Client: My son loves Minecraft and building things
Client: I want him to learn programming for the future
Client: It sounds fun and he would enjoy it
```

**Ожидаемый результат:**
- interests: `["game-based learning", "future skills"]`
- emotion: `"engaged"` или `"curious"`
- stage: `"profiling"` или `"presentation"`

### Тест 3: Извлечение потребности
```
Client: I want him to think more logically
Client: He needs to improve problem-solving skills
Client: I need him to be more confident
```

**Ожидаемый результат:**
- need: `"think more logically"` или `"improve problem-solving skills"`
- interests: `["logic"]` или `["confidence"]`

### Тест 4: Полный диалог (Profiling → Closing)
```
Client: My daughter is 12 years old
Manager: What are her interests?
Client: She loves games and wants to create her own
Manager: Has she tried coding before?
Client: No, but she's very creative and smart
Manager: Our program teaches game development with Python
Client: That sounds perfect! When can she start?
Manager: We have classes starting next week
Client: Great, how do we register?
```

**Ожидаемый результат:**
- stage: прогрессия от `"profiling"` → `"presentation"` → `"closing"`
- emotion: `"engaged"` (без возражений)
- interests: `["game-based learning", "creativity"]`
- engagement: высокий (~70-90%)
- trend: `"up"`

---

## 🔌 API Reference

### POST `/api/process-transcript`

Обрабатывает текстовый транскрипт.

**Request:**
```bash
curl -X POST http://localhost:8000/api/process-transcript \
  -F 'transcript=Client: My child is 10 years old...'
```

**Response:**
```json
{
  "success": true,
  "message": "Обработано 4 высказываний",
  "client_insight": {
    "stage": "profiling",
    "emotion": "curious",
    "active_objections": [],
    "interests": ["game-based learning"],
    "need": "think logically",
    "engagement": 0.65,
    "trend": "up"
  },
  "hint": "Предложите пробный урок...",
  "prob": 0.78
}
```

### POST `/api/process-video`

Обрабатывает видео файл.

**Request:**
```bash
curl -X POST http://localhost:8000/api/process-video \
  -F 'file=@/path/to/video.mp4'
```

**Response (пока):**
```json
{
  "success": false,
  "error": "Video processing not implemented yet.",
  "hint": "Use 'Paste Transcript' mode for now"
}
```

### POST `/api/process-youtube`

Обрабатывает YouTube видео.

**Request:**
```bash
curl -X POST http://localhost:8000/api/process-youtube \
  -F 'url=https://youtube.com/watch?v=...'
```

**Response (пока):**
```json
{
  "success": false,
  "error": "YouTube processing not implemented yet.",
  "hint": "Use 'Paste Transcript' mode for now"
}
```

---

## 🛠️ Реализация Video/YouTube (TODO)

Для добавления поддержки видео и YouTube потребуется:

### 1. Установить зависимости

```bash
cd backend

# FFmpeg для извлечения аудио
brew install ffmpeg  # Mac
# или apt-get install ffmpeg  # Linux

# Python библиотеки
pip install pydub yt-dlp faster-whisper

# Добавить в requirements.txt:
# pydub>=0.25.1
# yt-dlp>=2023.12.30
# faster-whisper>=0.10.0
```

### 2. Реализовать в backend/main.py

```python
from pydub import AudioSegment
import yt_dlp
from faster_whisper import WhisperModel

# Загрузить Whisper модель
whisper_model = WhisperModel("base", device="cpu")

@app.post("/api/process-video")
async def process_video(file: UploadFile = File(...)):
    # 1. Сохранить файл временно
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    # 2. Извлечь аудио через FFmpeg
    audio = AudioSegment.from_file(temp_path)
    audio_path = temp_path + ".wav"
    audio.export(audio_path, format="wav")
    
    # 3. Транскрибировать через Whisper
    segments, info = whisper_model.transcribe(audio_path)
    transcript = "\n".join([seg.text for seg in segments])
    
    # 4. Обработать как transcript
    return await process_transcript(transcript)
```

---

## 💡 Преимущества Debug Mode

✅ **Быстрое тестирование** - не нужен реальный звонок  
✅ **Повторяемость** - используйте одни и те же тесты  
✅ **Разработка** - тестируйте алгоритмы без ASR  
✅ **Демо** - показывайте систему без live sound  
✅ **Отладка** - проверяйте edge cases  

---

## 🔍 Troubleshooting

### Проблема: "Network error" при отправке транскрипта

**Решение:**
1. Убедитесь, что backend запущен на порту 8000
2. Проверьте в консоли браузера (F12)
3. Проверьте `frontend/.env`: `VITE_API_HTTP=http://localhost:8000`

### Проблема: Client Insights не обновляются

**Решение:**
1. Подключитесь к WebSocket `/coach` (кнопка "Начать запись" один раз)
2. Или обновите страницу и попробуйте снова
3. Backend должен отправлять updates через WebSocket

### Проблема: Ошибка "501 Not Implemented" для Video/YouTube

**Решение:**
Это нормально! Эти режимы пока не реализованы. Используйте режим **"📝 Text"** для отладки.

---

## 📝 Следующие шаги

### Phase 1: Text Mode ✅ **ГОТОВ**
- [x] UI с табами
- [x] Backend endpoint
- [x] Интеграция с insights analyzer
- [x] WebSocket broadcast

### Phase 2: Video Upload 🚧 **TODO**
- [ ] Установить FFmpeg + pydub
- [ ] Реализовать извлечение аудио
- [ ] Интегрировать faster-whisper
- [ ] Diarization (определение спикеров)

### Phase 3: YouTube Support 🚧 **TODO**
- [ ] Установить yt-dlp
- [ ] Скачивание видео
- [ ] Извлечение + транскрипция
- [ ] Кеширование результатов

---

**Используйте Debug Mode для быстрой разработки и тестирования! 🚀**

Начните с режима **📝 Text** — он работает уже сейчас!

