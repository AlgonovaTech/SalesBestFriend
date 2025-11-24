# 📚 SalesBestFriend - Полная Продуктово-Техническая Документация

**Версия:** 2.0  
**Дата:** 24 ноября 2025  
**Статус:** Production Ready

---

## 📋 Содержание

1. [Обзор Продукта](#1-обзор-продукта)
2. [Архитектура Системы](#2-архитектура-системы)
3. [Технический Стек](#3-технический-стек)
4. [Backend Компоненты](#4-backend-компоненты)
5. [Frontend Компоненты](#5-frontend-компоненты)
6. [Потоки Данных](#6-потоки-данных)
7. [AI/LLM Интеграция](#7-aillm-интеграция)
8. [Deployment](#8-deployment)
9. [Конфигурация](#9-конфигурация)
10. [Security & Permissions](#10-security--permissions)

---

## 1. Обзор Продукта

### 1.1 Что это такое?

**SalesBestFriend** — это AI-powered ассистент для продавцов, проводящих trial class (пробные уроки) по Zoom/Google Meet. Система работает в реальном времени, анализируя разговор на **индонезийском языке** и предоставляя:

- ✅ **Чеклист прогресса** — 7 стадий звонка с 25+ пунктами
- 🎯 **Тайминг стадий** — система подсказывает, когда вы отстаете от плана
- 👤 **Client Card** — автоматическое заполнение информации о клиенте
- 🎤 **Real-time транскрипция** — Whisper транскрибирует аудио каждые 3 секунды
- 🤖 **AI анализ** — Gemini 2.5 Flash проверяет выполнение пунктов и извлекает данные

### 1.2 Основные Use Cases

1. **Trial Class для онлайн-школы программирования** (основной сценарий)
   - Разговор с родителем + ребенком
   - Демонстрация платформы
   - Выявление потребностей
   - Закрытие на покупку пакета

2. **YouTube анализ** — загрузка записи звонка для post-mortem анализа

3. **Debug mode** — вставка готового текста для тестирования LLM

---

## 2. Архитектура Системы

### 2.1 High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        VERCEL (Frontend)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  React App (TypeScript + Vite)                         │ │
│  │  - UI Components                                       │ │
│  │  - WebSocket Clients                                   │ │
│  │  - MediaRecorder (Audio Capture)                      │ │
│  └─────────────────┬──────────────────────────────────────┘ │
└────────────────────┼──────────────────────────────────────────┘
                     │
            WebSocket │ (wss://)
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                    RAILWAY (Backend)                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  FastAPI Server (Python 3.11)                          │  │
│  │  - WebSocket Handlers (/ingest, /coach)               │  │
│  │  - Real-time Transcriber (Faster-Whisper)             │  │
│  │  - Trial Class Analyzer (LLM Integration)             │  │
│  └─────────────────┬──────────────────────────────────────┘  │
└────────────────────┼──────────────────────────────────────────┘
                     │
         HTTPS POST  │
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                  OpenRouter API                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Gemini 2.5 Flash (google/gemini-2.5-flash-preview)   │  │
│  │  - Checklist item completion detection                 │  │
│  │  - Client card field extraction                        │  │
│  │  - Evidence validation                                 │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 Communication Patterns

#### 2.2.1 Audio Ingestion Flow

```
Browser (MediaRecorder)
    │
    │ Binary WebM chunks (every 3s)
    ▼
WebSocket /ingest
    │
    ▼
AudioBuffer (in-memory queue)
    │
    │ Trigger on buffer size or timeout
    ▼
Faster-Whisper (local transcription)
    │
    │ Indonesian text
    ▼
accumulated_transcript (global state)
```

#### 2.2.2 Analysis & Update Flow

```
Backend Timer (every 5s)
    │
    ▼
Trial Class Analyzer
    │
    ├─> LLM Call #1: Check incomplete checklist items
    │   └─> For each item: check_checklist_item()
    │       └─> LLM validates evidence
    │
    ├─> LLM Call #2: Extract client card fields
    │   └─> extract_client_card_fields()
    │       └─> LLM validates evidence
    │
    └─> Build coach update message
        └─> Send via WebSocket /coach to all connected clients
```

#### 2.2.3 Frontend Update Flow

```
WebSocket /coach
    │
    │ JSON message
    ▼
React State Update
    │
    ├─> setStages(data.stages)           → StageChecklist component
    ├─> setClientCard(data.clientCard)   → ClientCard component
    ├─> setCallElapsed(...)               → CallTimer component
    └─> setDebugLogs(...)                 → DebugLogPanel component
```

---

## 3. Технический Стек

### 3.1 Backend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Python** | 3.11+ | Runtime |
| **FastAPI** | 0.109.0 | Web framework + WebSockets |
| **Uvicorn** | 0.27.0 | ASGI server |
| **Faster-Whisper** | 1.2.0 | Speech-to-text (Indonesian) |
| **CTranslate2** | 4.6.0 | Whisper inference engine |
| **Requests** | 2.31.0 | HTTP client для OpenRouter |
| **Python-dotenv** | 1.0.0 | Environment configuration |
| **PyDub** | 0.25.1 | Audio processing |
| **yt-dlp** | 2025.10.22 | YouTube audio extraction |

### 3.2 Frontend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **React** | 18.2.0 | UI framework |
| **TypeScript** | 5.3.3 | Type safety |
| **Vite** | 5.0.8 | Build tool + dev server |
| **CSS** | Native | Styling (no frameworks) |

### 3.3 External Services

| Сервис | Назначение | Модель |
|--------|------------|--------|
| **OpenRouter** | LLM API Gateway | Gemini 2.5 Flash |
| **Railway** | Backend hosting | Container deployment |
| **Vercel** | Frontend hosting | Edge deployment |

---

## 4. Backend Компоненты

### 4.1 Core Files

#### 4.1.1 `main_trial_class.py`

**Назначение:** Главный entry point FastAPI приложения

**Ключевые функции:**

1. **WebSocket `/ingest`** — прием аудио чанков
   ```python
   @app.websocket("/ingest")
   async def websocket_ingest(websocket: WebSocket):
       # Accepts binary audio chunks (WebM)
       # Buffers them in AudioBuffer
       # Triggers transcription on buffer threshold
   ```

2. **WebSocket `/coach`** — отправка обновлений UI
   ```python
   @app.websocket("/coach")
   async def websocket_coach(websocket: WebSocket):
       # Sends real-time updates:
       # - Call structure (stages, items)
       # - Client card data
       # - Timing status
       # - Debug logs
   ```

3. **Background Task: `analyze_conversation_loop()`**
   ```python
   async def analyze_conversation_loop():
       while True:
           await asyncio.sleep(5)  # Every 5 seconds
           # 1. Check incomplete checklist items
           # 2. Extract client card fields
           # 3. Broadcast updates to all /coach connections
   ```

4. **Transcription Handler: `handle_transcription()`**
   ```python
   def handle_transcription(text: str):
       global accumulated_transcript
       accumulated_transcript += text
       # Keep only last 1000 words for LLM context window
   ```

**Global State:**

```python
# WebSocket connections
coach_connections: Set[WebSocket] = set()

# Transcription state
accumulated_transcript: str = ""
transcription_language: str = "id"  # Indonesian
is_live_recording: bool = False

# Call structure
call_structure = get_default_call_structure()  # 7 stages
client_card_fields = get_default_client_card_fields()  # 11 fields

# Progress tracking
checklist_progress: Dict[str, bool] = {}
checklist_evidence: Dict[str, str] = {}
checklist_last_check: Dict[str, float] = {}

# Client data
client_card_data: Dict[str, Dict[str, str]] = {}

# Timing
call_start_time: Optional[float] = None
current_stage_id: str = ""
stage_start_time: Optional[float] = None
```

---

#### 4.1.2 `trial_class_analyzer.py`

**Назначение:** LLM-based анализ разговора

**Класс:** `TrialClassAnalyzer`

**Ключевые методы:**

1. **`check_checklist_item()`**
   ```python
   def check_checklist_item(
       self,
       item_id: str,
       item_content: str,
       item_type: str,  # "discuss" or "say"
       conversation_text: str
   ) -> Tuple[bool, float, str, Dict]:
       """
       Проверяет, выполнен ли пункт чеклиста
       
       Returns:
           (completed, confidence, evidence, debug_info)
       """
       # 1. Build prompt based on item type
       # 2. Call LLM with strict validation instructions
       # 3. Parse JSON response
       # 4. Apply guards:
       #    - Guard 1: Confidence must be >= 0.8
       #    - Guard 2: Evidence must be >= 10 chars
       #    - Guard 3: Validate evidence with second LLM call
       # 5. Return result
   ```

2. **`_validate_evidence_relevance()`**
   ```python
   def _validate_evidence_relevance(
       self,
       item_content: str,
       evidence: str,
       reasoning: str,
       item_type: str
   ) -> bool:
       """
       Второй проход LLM для валидации evidence
       
       Проверяет:
       - Evidence не является приветствием ("oke", "halo")
       - Evidence семантически связана с item_content
       - Evidence достаточно специфична
       """
       # Hard-coded filters
       invalid_phrases = ["oke", "ok", "baik", "ya", "halo", ...]
       introduction_patterns = ["nama saya", "saya adalah", ...]
       
       # Keyword-based semantic check
       keyword_checks = [
           {"triggers": ["age", "umur"], "required_in_evidence": ["umur", "tahun"]},
           ...
       ]
       
       # Final LLM validation
       response = self._call_llm(validation_prompt)
       return result.get("is_valid", False)
   ```

3. **`extract_client_card_fields()`**
   ```python
   def extract_client_card_fields(
       self,
       conversation_text: str,
       current_values: Dict[str, str]
   ) -> Dict[str, Dict[str, str]]:
       """
       Извлекает данные клиента из разговора
       
       Returns:
           {field_id: {value, evidence, confidence, label}}
       """
       # 1. Build field descriptions with hints
       # 2. Call LLM with strict anti-hallucination rules
       # 3. Filter out fields with existing values
       # 4. Apply guards:
       #    - Guard 0: Reject placeholder values ("tidak disebutkan")
       #    - Guard 1: Value must be substantial (>5 chars)
       #    - Guard 2: Confidence must be >= 0.7
       #    - Guard 3: Evidence must exist (>10 chars)
       #    - Guard 4: Validate evidence with second LLM call
       # 5. Return updates
   ```

4. **`_call_llm()`**
   ```python
   def _call_llm(
       self,
       prompt: str,
       temperature: float = 0.5,
       max_tokens: int = 500
   ) -> str:
       """
       Вызов OpenRouter API
       
       Model: google/gemini-2.5-flash-preview-09-2025
       Reason: Fastest, cheapest, good for Indonesian
       """
       response = requests.post(
           "https://openrouter.ai/api/v1/chat/completions",
           headers={"Authorization": f"Bearer {api_key}"},
           json={
               "model": self.model,
               "messages": [{"role": "user", "content": prompt}],
               "temperature": temperature,
               "max_tokens": max_tokens
           }
       )
       # Extract JSON from response (handles markdown wrapping)
   ```

**LLM Prompt Engineering:**

Система использует **multi-layer validation** для предотвращения ложных срабатываний:

1. **First LLM call**: Initial check с строгими инструкциями
2. **Hard-coded filters**: Фильтрация generic phrases ("oke", "baik")
3. **Semantic validation**: Проверка ключевых слов в evidence
4. **Second LLM call**: Валидация, что evidence действительно доказывает action

---

#### 4.1.3 `call_structure_config.py`

**Назначение:** Конфигурация структуры звонка

**Структура данных:**

```python
DEFAULT_CALL_STRUCTURE: List[CallStage] = [
    {
        "id": "stage_1_opening",
        "name": "Opening & Greeting",
        "startOffsetSeconds": 0,
        "durationSeconds": 120,  # 2 min
        "items": [
            {
                "id": "greet_client",
                "type": "say",  # "say" or "discuss"
                "content": "Greet the client warmly..."
            },
            ...
        ]
    },
    {
        "id": "stage_2_discovery",
        "name": "Understanding Needs",
        "startOffsetSeconds": 120,  # 2 min
        "durationSeconds": 300,  # 5 min
        "items": [...]
    },
    # ... 7 stages total
]
```

**Стадии звонка:**

1. **Opening & Greeting** (0-2 min) — 3 items
2. **Understanding Needs** (2-7 min) — 5 items
3. **Trial Class Introduction** (7-10 min) — 3 items
4. **Conducting Trial Class** (10-30 min) — 5 items
5. **Trial Feedback & Discussion** (30-35 min) — 4 items
6. **Address Concerns** (35-40 min) — 4 items
7. **Closing & Next Steps** (40-45 min) — 5 items

**Total:** 29 checklist items

**Функции:**

```python
def get_stage_by_time(elapsed_seconds: int) -> str:
    """Fallback: определение стадии по времени"""

def detect_stage_by_context(
    conversation_text: str,
    elapsed_seconds: int,
    analyzer
) -> str:
    """AI-based: определение стадии по контексту разговора"""

def get_stage_timing_status(stage_id: str, elapsed_seconds: int) -> Dict:
    """
    Returns:
        {
            "status": "on_time" | "slightly_late" | "very_late",
            "message": "On track" | "2 min behind"
        }
    """
```

---

#### 4.1.4 `client_card_config.py`

**Назначение:** Конфигурация полей Client Card

**Структура данных:**

```python
DEFAULT_CLIENT_CARD_FIELDS: List[ClientCardField] = [
    # Child Information
    {"id": "child_name", "label": "Child's Name", ...},
    {"id": "child_interests", "label": "Child's Interests", ...},
    {"id": "child_experience", "label": "Prior Experience", ...},
    
    # Parent Information
    {"id": "parent_goal", "label": "Parent's Goal", ...},
    {"id": "learning_motivation", "label": "Why Learning Now", ...},
    
    # Needs & Pain Points
    {"id": "main_pain_point", "label": "Main Pain Point", ...},
    {"id": "desired_outcome", "label": "Desired Outcome", ...},
    
    # Concerns & Objections
    {"id": "objections", "label": "Objections Raised", ...},
    {"id": "budget_constraint", "label": "Budget Situation", ...},
    {"id": "schedule_constraint", "label": "Schedule Constraints", ...},
    
    # Additional
    {"id": "additional_notes", "label": "Additional Notes", ...}
]
```

**LLM Extraction Hints:**

```python
LLM_EXTRACTION_HINTS = {
    "child_name": "Extract child's name and age (e.g. 'Budi, 10 years old')",
    "child_interests": "Games (Minecraft, Roblox), activities, subjects",
    "parent_goal": "What parent wants: skills, career prep, creativity?",
    ...
}
```

---

#### 4.1.5 `utils/realtime_transcriber.py`

**Назначение:** Whisper-based транскрипция аудио

**Ключевая функция:**

```python
async def transcribe_audio_buffer(
    audio_buffer: AudioBuffer,
    model_size: str = "base",
    language: str = "id",
    callback=None
):
    """
    Transcribes audio from buffer using Faster-Whisper
    
    Args:
        audio_buffer: AudioBuffer instance with queued chunks
        model_size: "tiny", "base", "small", "medium", "large"
        language: Language code ("id" for Indonesian)
        callback: Function to call with transcribed text
    
    Process:
        1. Combine all audio chunks in buffer
        2. Write to temporary .webm file
        3. Load with Faster-Whisper
        4. Transcribe (VAD filter enabled)
        5. Call callback with text
        6. Clear buffer
    """
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        audio_file,
        language=language,
        vad_filter=True,  # Voice Activity Detection
        vad_parameters=dict(
            min_silence_duration_ms=500,
            speech_pad_ms=200
        )
    )
```

**Модели Whisper:**

| Размер | Параметры | Скорость | Качество | Use Case |
|--------|-----------|----------|----------|----------|
| `tiny` | 39M | Fastest | Low | Quick tests |
| `base` | 74M | Fast | Good | **Production** ✅ |
| `small` | 244M | Medium | Better | High accuracy needed |
| `medium` | 769M | Slow | Best | Offline processing |

**Текущая конфигурация:** `base` модель для баланса скорости и точности.

---

#### 4.1.6 `utils/audio_buffer.py`

**Назначение:** Буферизация аудио чанков

```python
class AudioBuffer:
    """In-memory buffer for audio chunks"""
    
    def __init__(self):
        self.chunks: List[bytes] = []
        self.lock = asyncio.Lock()
    
    async def append(self, chunk: bytes):
        """Add audio chunk to buffer"""
        async with self.lock:
            self.chunks.append(chunk)
    
    async def get_all_and_clear(self) -> List[bytes]:
        """Get all chunks and clear buffer"""
        async with self.lock:
            result = self.chunks.copy()
            self.chunks.clear()
            return result
    
    def size(self) -> int:
        """Get number of chunks in buffer"""
        return len(self.chunks)
```

---

### 4.2 API Endpoints

#### HTTP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check + connections count |
| `GET` | `/call-structure` | Get current call structure config |
| `POST` | `/call-structure` | Update call structure (for settings) |
| `GET` | `/client-card-fields` | Get client card field definitions |
| `POST` | `/reset` | Reset all state (new call) |
| `POST` | `/youtube-process` | Process YouTube video URL |

#### WebSocket Endpoints

| Path | Direction | Description |
|------|-----------|-------------|
| `/ingest` | Client → Server | Audio chunks (binary WebM) |
| `/coach` | Server → Client | Real-time updates (JSON) |

---

## 5. Frontend Компоненты

### 5.1 Core Files

#### 5.1.1 `App_TrialClass.tsx`

**Назначение:** Главный компонент приложения

**State Management:**

```typescript
const [isRecording, setIsRecording] = useState(false)
const [status, setStatus] = useState<'idle' | 'connecting' | 'connected'>('idle')
const [callElapsed, setCallElapsed] = useState(0)  // seconds
const [stageElapsed, setStageElapsed] = useState(0)
const [currentStageId, setCurrentStageId] = useState<string>('')
const [stages, setStages] = useState<Stage[]>([])
const [clientCard, setClientCard] = useState<Record<string, string>>({})
const [debugLogs, setDebugLogs] = useState<DebugLogEntry[]>([])
const [selectedLanguage, setSelectedLanguage] = useState('id')
```

**WebSocket Connections:**

```typescript
// /coach WebSocket for receiving updates
const coachWs = new WebSocket(`${API_WS}/coach`)

coachWs.onmessage = (e) => {
    const data: CoachMessage = JSON.parse(e.data)
    setCallElapsed(data.callElapsedSeconds)
    setStages(data.stages)
    setClientCard(data.clientCard)
    setDebugLogs(data.debugLog || [])
}

// /ingest WebSocket for sending audio
const ingestWs = new WebSocket(`${API_WS}/ingest`)
```

**Audio Capture:**

```typescript
const startRecording = async () => {
    // Request tab audio capture
    const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true  // ⚠️ CRITICAL: Must enable audio
    })
    
    // Create MediaRecorder
    const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 16000
    })
    
    // Send chunks to /ingest
    mediaRecorder.ondataavailable = (e) => {
        if (ingestWs.readyState === WebSocket.OPEN) {
            ingestWs.send(e.data)  // Binary send
        }
    }
    
    // Start with 3s chunks
    mediaRecorder.start(3000)
}
```

**Local Timer:**

```typescript
useEffect(() => {
    if (isRecording && callStartTimeRef.current) {
        timerIntervalRef.current = setInterval(() => {
            const elapsed = Math.floor((Date.now() - callStartTimeRef.current!) / 1000)
            setCallElapsed(elapsed)
        }, 1000)
    }
}, [isRecording])
```

---

#### 5.1.2 `components/StageChecklist.tsx`

**Назначение:** Отображение стадий и чеклиста

**Props:**

```typescript
interface Props {
    stages: Stage[]
    currentStageId: string
    callElapsed: number
}
```

**Rendering Logic:**

```typescript
<div className="stage-checklist">
    {stages.map(stage => (
        <div className={`stage ${stage.isCurrent ? 'current' : ''}`}>
            <div className="stage-header">
                <h3>{stage.name}</h3>
                <div className={`timing-badge ${stage.timingStatus}`}>
                    {stage.timingMessage}
                </div>
            </div>
            
            <div className="checklist-items">
                {stage.items.map(item => (
                    <div className={`item ${item.completed ? 'completed' : ''}`}>
                        <input 
                            type="checkbox" 
                            checked={item.completed}
                            disabled
                        />
                        <span className="item-content">
                            {item.content}
                        </span>
                        {item.evidence && (
                            <div className="evidence">
                                💬 {item.evidence}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    ))}
</div>
```

**Timing Status Colors:**

- `on_time` → Green badge: "On track"
- `slightly_late` → Yellow badge: "Slightly behind"
- `very_late` → Red badge: "X min behind"
- `not_started` → Gray badge: "Starts in X min"

---

#### 5.1.3 `components/ClientCard.tsx`

**Назначение:** Отображение информации о клиенте

**Props:**

```typescript
interface Props {
    clientCard: Record<string, string>
}
```

**Layout:**

```typescript
<div className="client-card">
    <h2>👤 Client Information</h2>
    
    <div className="field-group">
        <h3>Child Info</h3>
        {renderField("child_name")}
        {renderField("child_interests")}
        {renderField("child_experience")}
    </div>
    
    <div className="field-group">
        <h3>Parent Goals</h3>
        {renderField("parent_goal")}
        {renderField("learning_motivation")}
    </div>
    
    <div className="field-group">
        <h3>Pain Points</h3>
        {renderField("main_pain_point")}
        {renderField("desired_outcome")}
    </div>
    
    <div className="field-group">
        <h3>Concerns</h3>
        {renderField("objections")}
        {renderField("budget_constraint")}
        {renderField("schedule_constraint")}
    </div>
</div>
```

**Auto-update:**

- Поля заполняются автоматически по мере анализа разговора
- Зеленая метка ✅ появляется при заполнении
- Evidence показывается при hover

---

#### 5.1.4 `components/CallTimer.tsx`

**Назначение:** Отображение таймера звонка

```typescript
interface Props {
    callElapsed: number  // seconds
    stageElapsed: number
    currentStageName: string
}

function CallTimer({ callElapsed, stageElapsed, currentStageName }: Props) {
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }
    
    return (
        <div className="call-timer">
            <div className="total-time">
                ⏱️ {formatTime(callElapsed)}
            </div>
            <div className="stage-info">
                📍 {currentStageName}
                <span className="stage-time">
                    ({formatTime(stageElapsed)})
                </span>
            </div>
        </div>
    )
}
```

---

#### 5.1.5 `components/DebugLogPanel.tsx`

**Назначение:** Отображение debug логов LLM решений

**Props:**

```typescript
interface DebugLogEntry {
    timestamp: string
    type: string  // "checklist_check" | "client_field_extracted" | ...
    [key: string]: any
}

interface Props {
    logs: DebugLogEntry[]
}
```

**Rendering:**

```typescript
<div className="debug-log-panel">
    <h3>🐛 Debug Log</h3>
    <div className="log-entries">
        {logs.map((log, i) => (
            <div className="log-entry">
                <div className="log-header">
                    <span className="timestamp">{log.timestamp}</span>
                    <span className="type">{log.type}</span>
                </div>
                <pre className="log-details">
                    {JSON.stringify(log, null, 2)}
                </pre>
            </div>
        ))}
    </div>
</div>
```

**Log Types:**

- `checklist_check`: LLM проверка пункта чеклиста
- `client_field_extracted`: Извлечено поле Client Card
- `validation_failed`: Evidence не прошла валидацию
- `stage_detected`: Определена новая стадия

---

### 5.2 Component Hierarchy

```
App_TrialClass.tsx
├── CallTimer
├── SettingsPanel (modal)
│   └── LanguageSelector
├── StageChecklist
│   └── ChecklistItem (inline)
├── ClientCard
│   └── ClientField (inline)
├── DebugLogPanel (collapsible)
└── YouTubeDebugPanel (modal)
```

---

## 6. Потоки Данных

### 6.1 Real-time Recording Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER ACTION: Click "Start Recording"                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. BROWSER: navigator.mediaDevices.getDisplayMedia()        │
│    - User selects Chrome tab                                 │
│    - MUST check "Share audio" ⚠️                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. MEDIARECORDER: Start recording                           │
│    - Format: audio/webm;codecs=opus                         │
│    - Chunk interval: 3 seconds                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. WEBSOCKET /ingest: Send binary chunks                    │
│    - ingestWs.send(audioBlob)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. BACKEND: AudioBuffer.append(chunk)                       │
│    - Buffer chunks in memory                                │
│    - Trigger transcription on:                              │
│      • Buffer size >= 5 chunks, OR                          │
│      • 10 seconds since last transcription                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. TRANSCRIPTION: Faster-Whisper                            │
│    - Combine chunks → .webm file                            │
│    - WhisperModel.transcribe(language="id")                 │
│    - VAD filter removes silence                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. ACCUMULATION: accumulated_transcript += text             │
│    - Keep last 1000 words                                   │
│    - Available for LLM analysis                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Analysis Loop Flow

```
┌─────────────────────────────────────────────────────────────┐
│ BACKGROUND TASK: Every 5 seconds                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. CHECK: is_live_recording == True?                        │
│    If False → skip iteration                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GET INCOMPLETE ITEMS:                                    │
│    items_to_check = [item for item in current_stage         │
│                      if not checklist_progress[item.id]]    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LLM ANALYSIS: For each incomplete item                   │
│    ┌────────────────────────────────────────────────────┐  │
│    │ analyzer.check_checklist_item()                     │  │
│    │   ├─> First LLM call: Check completion              │  │
│    │   ├─> Hard-coded filters                            │  │
│    │   └─> Second LLM call: Validate evidence            │  │
│    └────────────────────────────────────────────────────┘  │
│                                                             │
│    If completed == True:                                    │
│      checklist_progress[item_id] = True                     │
│      checklist_evidence[item_id] = evidence                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. CLIENT CARD EXTRACTION:                                  │
│    ┌────────────────────────────────────────────────────┐  │
│    │ analyzer.extract_client_card_fields()               │  │
│    │   ├─> Single LLM call for all fields               │  │
│    │   ├─> Filter out existing values                    │  │
│    │   └─> Validate each field's evidence                │  │
│    └────────────────────────────────────────────────────┘  │
│                                                             │
│    For each extracted field:                                │
│      client_card_data[field_id] = {value, evidence, ...}    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. BUILD UPDATE MESSAGE:                                    │
│    {                                                        │
│      "type": "update",                                      │
│      "callElapsedSeconds": elapsed,                         │
│      "currentStageId": current_stage_id,                    │
│      "stages": [...],  // with completed status            │
│      "clientCard": {...},  // field values                 │
│      "debugLog": [...]  // LLM decision logs               │
│    }                                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. BROADCAST: Send to all /coach WebSocket connections     │
│    for ws in coach_connections:                             │
│        await ws.send_json(update)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. FRONTEND UPDATE: React state refresh                    │
│    - StageChecklist: Check completed items                  │
│    - ClientCard: Display new fields                         │
│    - CallTimer: Update elapsed time                         │
│    - DebugLogPanel: Show new logs                           │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Stage Detection Flow

```
┌─────────────────────────────────────────────────────────────┐
│ TRIGGER: Every analysis iteration (5s)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. CHECK: Should we detect stage?                          │
│    - Time-based: Every 30 seconds                          │
│    - Context-based: When transcript changes significantly  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GET CONTEXT:                                             │
│    - Recent transcript (last 2000 chars)                    │
│    - Current call elapsed time                              │
│    - Previous stage ID                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DETECT STAGE:                                            │
│    detect_stage_by_context()                                │
│      ├─> Guard: Transcript too short? → Use first stage    │
│      ├─> LLM analysis of conversation topics               │
│      ├─> Confidence check (>= 0.6)                         │
│      └─> Fallback: Time-based detection                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. UPDATE STAGE:                                            │
│    if new_stage_id != current_stage_id:                     │
│        current_stage_id = new_stage_id                      │
│        stage_start_time = time.time()                       │
│        # Mark stage as "current" in UI                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. AI/LLM Интеграция

### 7.1 Model Selection

**Current Model:** `google/gemini-2.5-flash-preview-09-2025`

**Reasoning:**

| Критерий | Оценка | Комментарий |
|----------|--------|-------------|
| **Cost** | ⭐⭐⭐⭐⭐ | $0.10 / 1M input tokens |
| **Speed** | ⭐⭐⭐⭐⭐ | Fastest Gemini model |
| **Quality** | ⭐⭐⭐⭐ | Good for structured tasks |
| **Indonesian** | ⭐⭐⭐⭐⭐ | Excellent multilingual support |
| **JSON Mode** | ⭐⭐⭐⭐ | Reliable JSON responses |

**Alternative Models:**

- `anthropic/claude-3.5-sonnet` — Better quality, but 50x more expensive
- `meta-llama/llama-3.1-8b-instruct` — Cheaper, but worse Indonesian support
- `openai/gpt-4o-mini` — Good alternative, slightly more expensive

### 7.2 Prompt Engineering Strategies

#### 7.2.1 Type-Specific Instructions

```python
if item_type == "discuss":
    type_check = """
    This means you must find:
    ✅ A QUESTION being asked, OR
    ✅ An ANSWER that proves the question was asked
    
    BAD examples:
    - "Anak suka belajar" ✗ (no question)
    - "Nanti kita diskusi" ✗ (promise, not actual discussion)
    """
else:  # "say"
    type_check = """
    This means you must find:
    ✅ The manager STATING or EXPLAINING something
    
    BAD examples:
    - "Mau tau cara kerja?" ✗ (asking, not explaining)
    - "Nanti saya jelaskan" ✗ (promise to explain)
    """
```

#### 7.2.2 Anti-Hallucination Rules

```python
prompt += """
CRITICAL VALIDATION RULES:
1. Evidence must be a DIRECT QUOTE from conversation
2. Evidence must CLEARLY AND OBVIOUSLY show action was done
3. Generic phrases like "oke", "baik" are NEVER valid evidence
4. Greetings are NEVER valid evidence
5. Promises to do something are NOT completion
6. If you're even 20% unsure → mark completed=false

BE EXTREMELY CONSERVATIVE. When in doubt, mark as NOT completed.
"""
```

#### 7.2.3 Confidence Guidelines

```python
prompt += """
CONFIDENCE GUIDELINES:
- 90-100%: Action CLEARLY done, evidence is perfect
- 70-89%: Likely done, evidence is good but not perfect
- 50-69%: Possibly done, evidence is weak
- <50%: Probably not done or no evidence
"""
```

#### 7.2.4 Few-Shot Examples

```python
prompt += """
EXAMPLES:

✅ GOOD:
Action: "Ask about child's age"
Evidence: "Anaknya berapa tahun?"
Reasoning: Direct question about age

✅ GOOD:
Action: "Identify parent concerns"
Evidence: "Papa khawatir anak kurang fokus"
Reasoning: Clearly states a concern

❌ BAD:
Action: "Ask about child's age"
Evidence: "Oke, selamat datang"
Reasoning: Just a greeting, no connection to age

❌ BAD:
Action: "Explain curriculum"
Evidence: "Mau tau kurikulum kami?"
Reasoning: Asking, not explaining
"""
```

### 7.3 Error Handling & Retries

```python
try:
    response = self._call_llm(prompt)
    result = json.loads(response)
except requests.exceptions.Timeout:
    print("⚠️ LLM timeout, skipping this check")
    return False, 0.0, "Timeout", {}
except requests.exceptions.RequestException as e:
    print(f"⚠️ LLM API error: {e}")
    return False, 0.0, str(e), {}
except json.JSONDecodeError:
    print("⚠️ LLM returned invalid JSON")
    # Try to extract JSON from markdown
    if "```json" in response:
        content = response.split("```json")[1].split("```")[0].strip()
        result = json.loads(content)
    else:
        return False, 0.0, "Invalid JSON", {}
```

### 7.4 Cost Optimization

**Current Usage:**

- **Checklist checks:** ~5-10 LLM calls per analysis cycle (5s)
  - First pass: ~200 tokens per check
  - Validation pass: ~150 tokens per validation
  
- **Client card extraction:** 1 LLM call per analysis cycle
  - ~800 tokens per call

**Estimated Cost per Hour:**

```
Checklist: 10 calls/cycle × 12 cycles/min × 60 min × 350 tokens = 2.52M tokens
Client Card: 1 call/cycle × 12 cycles/min × 60 min × 800 tokens = 0.58M tokens

Total: ~3.1M tokens/hour × $0.10/1M = $0.31/hour
```

**Optimization Strategies:**

1. ✅ **Use Gemini Flash** instead of Claude (50x cheaper)
2. ✅ **Check only incomplete items** (not rechecking completed ones)
3. ✅ **Skip client card if no new transcript** (context length check)
4. ⏳ **Batch multiple items in single call** (future improvement)
5. ⏳ **Increase analysis interval** to 10s instead of 5s (future improvement)

---

## 8. Deployment

### 8.1 Backend (Railway)

**Platform:** Railway (https://railway.app)

**Configuration File:** `railway.toml`

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn backend.main_trial_class:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**Environment Variables:**

```bash
OPENROUTER_API_KEY=sk-or-v1-...
PORT=8000  # Auto-set by Railway
```

**Build Process:**

1. Railway detects Python project
2. Installs dependencies from `requirements.txt`
3. Downloads Whisper model (`base`) on first run
4. Starts Uvicorn server
5. Health check at `/health`

**Domain:**

- Production: `https://salesbestfriend-production.up.railway.app`
- WebSocket: `wss://salesbestfriend-production.up.railway.app`

**Monitoring:**

- Railway Dashboard: Logs, metrics, deployments
- Health endpoint: `GET /health` returns:
  ```json
  {
    "status": "healthy",
    "coach_connections": 1,
    "is_recording": true
  }
  ```

---

### 8.2 Frontend (Vercel)

**Platform:** Vercel (https://vercel.com)

**Configuration File:** `vercel.json`

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite"
}
```

**Environment Variables:**

```bash
# Set in Vercel dashboard under Settings → Environment Variables
VITE_API_WS=wss://salesbestfriend-production.up.railway.app
```

**Build Process:**

1. Vercel detects Vite project
2. Runs `npm install` in `frontend/`
3. Runs `npm run build` (TypeScript compilation + Vite build)
4. Deploys `dist/` folder to edge network
5. Automatic HTTPS + CDN

**Domain:**

- Production: Assigned by Vercel (e.g., `salesbestfriend-xxx.vercel.app`)
- Custom domain: Can be configured in Vercel settings

**Automatic Deployments:**

- **Main branch** → Production deployment
- **Pull requests** → Preview deployments
- **Rollback** available in Vercel dashboard

---

### 8.3 Deployment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DEVELOPER: Push to GitHub                                │
│    git push origin main                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ 2. RAILWAY       │    │ 2. VERCEL        │
│ (Backend)        │    │ (Frontend)       │
│                  │    │                  │
│ - Detect change  │    │ - Detect change  │
│ - Build image    │    │ - npm install    │
│ - Run tests      │    │ - npm run build  │
│ - Deploy         │    │ - Deploy to CDN  │
└────────┬─────────┘    └─────────┬────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│ 3. HEALTH CHECK  │    │ 3. SMOKE TEST    │
│ GET /health      │    │ Load homepage    │
└────────┬─────────┘    └─────────┬────────┘
         │                        │
         │                        │
         └────────────┬───────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PRODUCTION LIVE ✅                                       │
│ - Frontend: https://salesbestfriend.vercel.app              │
│ - Backend: https://salesbestfriend-production.up.railway.app│
└─────────────────────────────────────────────────────────────┘
```

---

### 8.4 Rollback Procedure

**If production breaks:**

1. **Railway:**
   - Go to Railway dashboard
   - Click on deployment history
   - Click "Redeploy" on last working version
   
2. **Vercel:**
   - Go to Vercel dashboard → Deployments
   - Find last working deployment
   - Click "Promote to Production"

3. **GitHub:**
   - Revert commit: `git revert <commit-hash>`
   - Push: `git push origin main`
   - Wait for auto-redeploy

---

## 9. Конфигурация

### 9.1 Environment Variables

#### Backend (`backend/.env`)

```bash
# OpenRouter API Key (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-...

# Optional: Model override (default: gemini-2.5-flash)
# LLM_MODEL=anthropic/claude-3.5-sonnet

# Optional: Whisper model size (default: base)
# WHISPER_MODEL_SIZE=small

# Optional: Analysis interval (default: 5)
# ANALYSIS_INTERVAL_SECONDS=10

# Optional: Transcription language (default: id)
# TRANSCRIPTION_LANGUAGE=id
```

#### Frontend (`frontend/.env`)

```bash
# Backend WebSocket URL
VITE_API_WS=ws://localhost:8000  # Development
# VITE_API_WS=wss://salesbestfriend-production.up.railway.app  # Production
```

### 9.2 Call Structure Customization

**Location:** `backend/call_structure_config.py`

**How to modify:**

1. Edit `DEFAULT_CALL_STRUCTURE` list
2. Add/remove stages
3. Add/remove items within stages
4. Change timing (`startOffsetSeconds`, `durationSeconds`)

**Example:**

```python
{
    "id": "stage_8_payment",  # New stage
    "name": "Payment Processing",
    "startOffsetSeconds": 2700,  # 45 min
    "durationSeconds": 300,  # 5 min
    "items": [
        {
            "id": "explain_payment_options",
            "type": "say",
            "content": "Explain available payment methods"
        },
        {
            "id": "process_payment",
            "type": "discuss",
            "content": "Process payment or schedule it"
        }
    ]
}
```

### 9.3 Client Card Customization

**Location:** `backend/client_card_config.py`

**How to modify:**

1. Edit `DEFAULT_CLIENT_CARD_FIELDS` list
2. Add/remove fields
3. Update LLM extraction hints in `LLM_EXTRACTION_HINTS`

**Example:**

```python
{
    "id": "child_school",
    "label": "Child's School",
    "hint": "Name of school and type (public/private/homeschool)",
    "multiline": False,
    "category": "child_info"
}

# Add to extraction hints:
LLM_EXTRACTION_HINTS["child_school"] = "Extract school name and type if mentioned"
```

---

## 10. Security & Permissions

### 10.1 API Key Security

**OpenRouter API Key:**

- ✅ Stored in `.env` (not in git)
- ✅ Only accessible by backend
- ✅ Transmitted over HTTPS to OpenRouter
- ⚠️ **Never exposed to frontend**

**Best Practices:**

1. Rotate keys periodically (monthly)
2. Use separate keys for dev/prod
3. Monitor usage on OpenRouter dashboard
4. Set spending limits in OpenRouter settings

### 10.2 CORS Configuration

**Current Settings:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Production Recommendations:**

```python
# Option 1: Restrict to specific domains
allow_origins=[
    "https://salesbestfriend.vercel.app",
    "http://localhost:3000"  # Dev only
]

# Option 2: Use environment variable
allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(",")
```

### 10.3 WebSocket Security

**Current State:**

- ❌ No authentication
- ❌ No rate limiting
- ✅ HTTPS/WSS encryption in production

**Production Recommendations:**

1. **Add authentication:**
   ```python
   @app.websocket("/ingest")
   async def websocket_ingest(websocket: WebSocket, token: str):
       if not verify_token(token):
           await websocket.close(code=403)
           return
   ```

2. **Rate limiting:**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @limiter.limit("60/minute")
   @app.websocket("/ingest")
   async def websocket_ingest(...):
       ...
   ```

3. **Connection limits:**
   ```python
   MAX_CONNECTIONS = 10
   if len(coach_connections) >= MAX_CONNECTIONS:
       await websocket.close(code=503)
   ```

### 10.4 Data Privacy

**Current State:**

- ✅ No data persistence (all in memory)
- ✅ Data cleared on server restart
- ✅ No logging of sensitive info
- ❌ No encryption of in-memory data

**If adding persistence:**

1. Encrypt sensitive fields (names, contact info)
2. Comply with GDPR (right to deletion, data export)
3. Add user consent for recording
4. Implement data retention policy

---

## 📌 Appendix

### A. Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `backend/main_trial_class.py` | FastAPI server + WebSockets | ~800 |
| `backend/trial_class_analyzer.py` | LLM analysis logic | ~935 |
| `backend/call_structure_config.py` | Call stages config | ~413 |
| `backend/client_card_config.py` | Client card fields config | ~216 |
| `backend/utils/realtime_transcriber.py` | Whisper transcription | ~150 |
| `backend/utils/audio_buffer.py` | Audio buffering | ~50 |
| `frontend/src/App_TrialClass.tsx` | Main React app | ~485 |
| `frontend/src/components/StageChecklist.tsx` | Checklist UI | ~200 |
| `frontend/src/components/ClientCard.tsx` | Client card UI | ~150 |

### B. External Dependencies

**Backend:**

- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `faster-whisper` — Speech-to-text
- `ctranslate2` — Whisper inference
- `requests` — HTTP client
- `python-dotenv` — Env config
- `pydub` — Audio processing
- `yt-dlp` — YouTube downloader

**Frontend:**

- `react` — UI library
- `react-dom` — React rendering
- `typescript` — Type safety
- `vite` — Build tool

### C. Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Transcription Latency** | 3-5s | Time from audio chunk to text |
| **LLM Response Time** | 1-3s | Gemini Flash response time |
| **Analysis Cycle** | 5s | How often LLM runs |
| **WebSocket Latency** | <100ms | Frontend ↔ Backend |
| **Memory Usage (Backend)** | ~500MB | With Whisper base model loaded |
| **CPU Usage (Backend)** | 20-40% | During active transcription |

### D. Known Limitations

1. **Single user session** — No multi-user support
2. **No persistence** — All data lost on restart
3. **Indonesian only** — Optimized for Indonesian language
4. **Whisper base model** — Balance of speed vs accuracy
5. **5s analysis cycle** — Not real-time item completion detection
6. **No authentication** — Anyone can connect to WebSockets
7. **Memory-only storage** — Limited by server RAM

### E. Future Improvements

1. **Multi-user support** — Session management per user
2. **Persistent storage** — PostgreSQL for call history
3. **Authentication** — JWT tokens for WebSocket connections
4. **Batch LLM calls** — Check multiple items in single call
5. **Faster analysis cycle** — Optimize to 2-3s
6. **Better Whisper model** — Medium or Large for accuracy
7. **Multilingual support** — English, Spanish, etc.
8. **Export functionality** — PDF/CSV export of call data
9. **Analytics dashboard** — Call performance metrics
10. **Custom playbooks** — User-editable call structures

---

## 🎉 Заключение

**SalesBestFriend** — это production-ready система для real-time AI-коучинга продавцов.

**Ключевые достижения:**

- ✅ **Real-time transcription** с Whisper
- ✅ **AI-powered analysis** с Gemini 2.5 Flash
- ✅ **Multi-layer validation** для точности
- ✅ **Production deployment** на Railway + Vercel
- ✅ **Indonesian language** оптимизация
- ✅ **Cost-effective** ($0.31/hour)

**Готово к использованию:**

1. Клонировать репозиторий
2. Настроить `.env` с API ключом
3. Запустить backend (`uvicorn main:app`)
4. Запустить frontend (`npm run dev`)
5. Начать trial class звонок!

---

**Версия документации:** 2.0  
**Последнее обновление:** 24 ноября 2025  
**Статус:** Production Ready ✅

