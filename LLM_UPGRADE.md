# 🧠 LLM-Powered Semantic Analysis

## Что изменилось

Система **больше НЕ использует ключевые слова**! Теперь все анализируется через **Claude 3 Haiku** с глубоким пониманием смысла.

---

## Новые возможности

### 1. **Speaker Diarization** 🎭
LLM автоматически определяет КТО говорит (клиент или продавец):

```python
segments = llm_analyzer.identify_speakers(transcript)
# Результат:
[
    {"speaker": "sales", "text": "Hello, my name is John"},
    {"speaker": "client", "text": "Hi, nice to meet you"}
]
```

**Без тренировки модели!** LLM понимает контекст разговора.

---

### 2. **Semantic Client Analysis** 🧠
Глубокий анализ настроения и намерений клиента:

```python
insight = llm_analyzer.analyze_client_sentiment(client_text, context)
# Результат:
{
    "emotion": "hesitant",
    "objections": ["price", "time"],
    "interests": ["future skills", "game-based learning"],
    "need_statement": "wants child to learn logical thinking",
    "engagement_level": 0.75,
    "buying_signals": ["sounds interesting", "tell me more"],
    "concerns": ["budget concerns", "time commitment"],
    "stage_hint": "objection"
}
```

**Понимает СМЫСЛ**, а не просто ищет слова!

---

### 3. **Semantic Checklist Matching** ✅
Проверка чеклиста на основе понимания, а не keywords:

```python
completed, reason = llm_analyzer.check_checklist_item_semantic(
    item_description="Introduce yourself and company",
    conversation_text="...",
    language="id"
)
# LLM понимает что "Halo, nama saya Budi dari CodeSchool" = представление!
```

**Работает на ЛЮБОМ языке** с пониманием культурных особенностей.

---

### 4. **Contextual Next Step** 💡
Умные рекомендации на основе всей ситуации:

```python
next_step = llm_analyzer.generate_next_step(
    current_stage="objection",
    client_insights={"objections": ["price"], "emotion": "hesitant"},
    checklist_progress={...},
    recent_conversation="..."
)
# "Address budget concerns with flexible payment options"
```

**Адаптируется** к реальному контексту разговора!

---

## Технические детали

### Модель: **Claude 3 Haiku**
- **Скорость:** 2-3x быстрее Sonnet
- **Цена:** $0.25/1M input (~12x дешевле Sonnet)
- **Качество:** Отличное понимание контекста
- **Latency:** ~1-2 seconds per call

### Fallback механизм
Если LLM не доступен → автоматический fallback на keywords:

```python
try:
    # LLM analysis
    result = llm_analyzer.analyze(...)
except Exception:
    # Fallback to keywords
    result = keyword_based_analysis(...)
```

**Система всегда работает!**

---

## Конфигурация

### `.env`

```bash
# OpenRouter API key (тот же что был)
OPENROUTER_API_KEY=sk-or-v1-...

# LLM model для семантического анализа
LLM_MODEL=anthropic/claude-3-haiku

# Включить LLM анализ (true/false)
USE_LLM_ANALYSIS=true
```

### Выбор модели

```bash
# Рекомендуется (default):
LLM_MODEL=anthropic/claude-3-haiku

# Лучшее качество (дороже):
LLM_MODEL=anthropic/claude-3.5-sonnet

# Еще дешевле:
LLM_MODEL=openai/gpt-4o-mini

# БЕСПЛАТНО:
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

---

## Workflow

```
Audio → Whisper Transcription
   ↓
LLM Speaker Diarization 🎭
   ↓ ↙ ↘
Client segments  |  Sales segments
   ↓
LLM Semantic Analysis 🧠
   ↓ ↙ ↘
Emotion | Objections | Interests | Stage
   ↓
LLM Checklist Matching ✅
   ↓
LLM Next Step Generation 💡
   ↓
WebSocket → UI Update
```

---

## Примеры

### Пример 1: Понимание косвенных возражений

**Клиент:** "Saya harus diskusi dengan suami dulu..."
("I need to discuss with my husband first...")

**Keywords:** ❌ Не найдет возражение
**LLM:** ✅ `objections: ["family"]`, `emotion: "hesitant"`

---

### Пример 2: Checklist на Bahasa Indonesia

**Чеклист:** "Introduce yourself and company"
**Разговор:** "Halo, nama saya Budi. Saya dari CodeSchool Indonesia."

**Keywords:** ❌ Нужны точные слова "introduce", "company"
**LLM:** ✅ Понимает что это представление!

---

### Пример 3: Контекстные рекомендации

**Ситуация:**
- Stage: objection
- Client: defensive, objection=price
- Progress: 3/10 items completed

**Keywords:** "Продолжайте презентацию"
**LLM:** ✅ "Offer payment plan to address budget concerns"

---

## Performance

### Latency
- **LLM call:** ~1-2 seconds
- **Total:** ~10-12 seconds per analysis cycle
- **Можно улучшить:** параллельные вызовы

### Cost (на 1 час звонка)
- **Транскрипция:** ~10,000 слов = ~13K tokens
- **3 LLM calls/min × 60 min = 180 calls**
- **~500 tokens per call = 90K tokens**
- **Cost:** $0.0225 (~2 цента!)

**Очень дешево!** 🎉

---

## Отключение LLM

Если хотите вернуться к keywords:

```bash
USE_LLM_ANALYSIS=false
```

Или удалите `LLM_MODEL` из `.env`.

---

## Roadmap

- [ ] Параллельные LLM calls для снижения latency
- [ ] Кеширование повторяющихся ответов
- [ ] Fine-tuning на реальных sales call data
- [ ] Integration с pyannote.audio для точной diarization
- [ ] Streaming responses для real-time

---

**MVP готов с LLM! 🚀**

Теперь система понимает **СМЫСЛ** разговора, а не просто ищет слова!

