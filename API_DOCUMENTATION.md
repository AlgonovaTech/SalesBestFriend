# 🚀 Trial Class Sales Assistant - API Documentation

**Version:** 2.0.0  
**Service:** Real-time Zoom Trial Class Coaching  
**Language:** Bahasa Indonesia (id)  
**UI Language:** English

---

## 📡 Base URLs

### Local Development
```
HTTP: http://localhost:8000
WebSocket: ws://localhost:8000
```

### Production (Railway)
```
HTTP: https://salesbestfriend-production.up.railway.app
WebSocket: wss://salesbestfriend-production.up.railway.app
```

---

## 🔌 WebSocket Endpoints

### 1. `/ingest` - Audio Stream Ingestion

**Purpose:** Receive real-time audio chunks from frontend (PCM 16kHz mono)

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ingest')
```

**Message Format (Client → Server):**
```javascript
// Binary PCM audio chunks (Int16Array)
ws.send(pcmChunk.buffer)
```

**Response (Server → Client):**
```json
{
  "type": "transcript_update",
  "transcript": "Selamat pagi, nama saya...",
  "is_final": false
}
```

**Features:**
- Real-time transcription using Faster Whisper
- Automatic language detection (Bahasa Indonesia)
- Speaker diarization (sales manager vs client)
- Buffered processing for efficiency

---

### 2. `/coach` - Real-time Coaching Data

**Purpose:** Stream coaching insights, checklist updates, client info

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/coach')
```

**Messages (Server → Client):**

#### 2.1 Session Initialization
```json
{
  "type": "session_started",
  "session_id": "abc123",
  "message": "Coaching session started"
}
```

#### 2.2 Checklist Progress Update
```json
{
  "type": "checklist_update",
  "stages": [
    {
      "id": "greeting",
      "name": "Greeting & Rapport",
      "time_budget_seconds": 120,
      "items": [
        {
          "id": "intro_self",
          "type": "ask",
          "label": "Introduce yourself & company",
          "completed": true,
          "confidence": 0.95
        }
      ]
    }
  ],
  "currentStageId": "greeting",
  "callElapsedSeconds": 45
}
```

#### 2.3 Client Card Update
```json
{
  "type": "client_card_update",
  "clientCard": {
    "child_age": "8 years old",
    "child_interests": "Minecraft, Roblox",
    "parent_goal": "Wants child to learn programming",
    "main_pain_point": "Child spends too much time on games",
    "budget_range": "500-1000k IDR/month",
    "buying_signals": "Asked about trial class schedule"
  }
}
```

#### 2.4 In-Call Assist (Real-time Hints)
```json
{
  "type": "assist",
  "trigger": "objection_detected",
  "message": "Client mentioned budget concerns. Suggest payment plan option.",
  "priority": "high"
}
```

#### 2.5 Error Message
```json
{
  "type": "error",
  "error": "Transcription service unavailable"
}
```

**Messages (Client → Server):**

#### 2.6 Update Configuration
```json
{
  "type": "update_config",
  "call_structure": [...],
  "client_fields": {...}
}
```

---

## 📋 HTTP REST Endpoints

### 3. `GET /` - Service Info

**Response:**
```json
{
  "service": "Trial Class Sales Assistant",
  "version": "2.0.0",
  "status": "operational"
}
```

---

### 4. `GET /health` - Health Check

**Response:**
```json
{
  "status": "healthy",
  "transcription": "ready",
  "llm": "ready"
}
```

---

### 5. `GET /api/config/call-structure` - Get Call Structure

**Purpose:** Retrieve current call structure configuration (stages, items, time budgets)

**Response:**
```json
{
  "stages": [
    {
      "id": "greeting",
      "name": "Greeting & Rapport",
      "time_budget_seconds": 120,
      "items": [
        {
          "id": "intro_self",
          "type": "ask",
          "label": "Introduce yourself & company"
        },
        {
          "id": "check_time",
          "type": "ask",
          "label": "Check client's availability"
        }
      ]
    },
    {
      "id": "discovery",
      "name": "Discovery & Needs",
      "time_budget_seconds": 300,
      "items": [...]
    }
  ]
}
```

---

### 6. `POST /api/config/call-structure` - Update Call Structure

**Purpose:** Update call structure configuration from frontend Settings

**Request Body:**
```json
{
  "stages": [
    {
      "id": "greeting",
      "name": "Greeting & Rapport",
      "time_budget_seconds": 120,
      "items": [
        {
          "id": "intro_self",
          "type": "ask",
          "label": "Introduce yourself & company"
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Call structure updated successfully"
}
```

---

### 7. `GET /api/config/client-card` - Get Client Card Fields

**Purpose:** Retrieve client card field configuration

**Response:**
```json
{
  "fields": {
    "Child Information": [
      {
        "id": "child_age",
        "label": "Child's Age",
        "type": "text",
        "hint": "Age of the child"
      },
      {
        "id": "child_interests",
        "label": "Child's Interests",
        "type": "text",
        "hint": "What the child likes (games, subjects)"
      }
    ],
    "Parent Information": [
      {
        "id": "parent_goal",
        "label": "Parent's Main Goal",
        "type": "textarea",
        "hint": "What the parent wants the child to achieve"
      }
    ]
  }
}
```

---

### 8. `POST /api/config/client-card` - Update Client Card Fields

**Purpose:** Update client card field configuration from frontend Settings

**Request Body:**
```json
{
  "fields": {
    "Child Information": [
      {
        "id": "child_age",
        "label": "Child's Age",
        "type": "text",
        "hint": "Age of the child"
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Client card fields updated successfully"
}
```

---

### 9. `POST /api/process-youtube` - Debug: YouTube Analysis

**Purpose:** Process a YouTube URL for debugging (offline analysis)

**Request (multipart/form-data):**
```
url: https://youtube.com/watch?v=...
language: id
```

**Response:**
```json
{
  "success": true,
  "transcriptLength": 5432,
  "currentStage": "discovery",
  "itemsCompleted": 12,
  "totalItems": 25,
  "clientCardFields": 8,
  "transcript": "Full transcript text...",
  "analysis": {
    "stages": [...],
    "clientCard": {...}
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to download video: Invalid URL"
}
```

---

### 10. `POST /api/process-transcript` - Debug: Text Analysis

**Purpose:** Process raw transcript text for debugging

**Request (multipart/form-data):**
```
transcript: "Selamat pagi, nama saya..."
language: id
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "stages": [...],
    "clientCard": {...}
  }
}
```

---

## 🎯 Data Models

### Call Stage
```typescript
interface CallStage {
  id: string              // Unique identifier (e.g., "greeting")
  name: string           // Display name (e.g., "Greeting & Rapport")
  time_budget_seconds: number  // Recommended time budget
  items: ChecklistItem[]
}
```

### Checklist Item
```typescript
interface ChecklistItem {
  id: string             // Unique identifier (e.g., "intro_self")
  type: "ask" | "say"   // Type: ask question or explain something
  label: string          // What to ask/say (e.g., "Ask about child's age")
  hint?: string          // Optional hint for AI (e.g., "Age in years")
  completed?: boolean    // Completion status (AI-driven)
  confidence?: number    // AI confidence (0-1)
}
```

### Client Card Field
```typescript
interface ClientCardField {
  id: string             // Unique identifier (e.g., "child_age")
  label: string          // Display label (e.g., "Child's Age")
  type: "text" | "textarea"  // Input type
  hint?: string          // Hint for AI extraction
  value?: string         // Current value (AI-filled)
}
```

### Client Card (Grouped)
```typescript
interface ClientCard {
  [category: string]: ClientCardField[]
}

// Example:
{
  "Child Information": [
    { id: "child_age", label: "Child's Age", type: "text" }
  ],
  "Parent Information": [
    { id: "parent_goal", label: "Parent's Goal", type: "textarea" }
  ]
}
```

---

## 🔐 Authentication

**Current:** No authentication (MVP)  
**Future:** API keys, JWT tokens for production

---

## 📊 Rate Limits

**Current:** No rate limits (MVP)  
**Recommended for Production:**
- WebSocket connections: 10 per IP
- HTTP requests: 100 per minute per IP

---

## 🧪 Testing Endpoints

### Test Backend Availability
```bash
curl http://localhost:8000/
```

### Test Health
```bash
curl http://localhost:8000/health
```

### Test Get Config
```bash
curl http://localhost:8000/api/config/call-structure
curl http://localhost:8000/api/config/client-card
```

### Test YouTube Processing
```bash
curl -X POST http://localhost:8000/api/process-youtube \
  -F "url=https://youtube.com/watch?v=..." \
  -F "language=id"
```

---

## 🛠️ Error Codes

| HTTP Status | Meaning |
|------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Endpoint not found |
| 500 | Internal Server Error |
| 502 | Backend unavailable (Railway) |

---

## 📚 Related Documentation

- `PRODUCT_ARCHITECTURE.md` - System architecture
- `YOUTUBE_DEBUG_GUIDE.md` - How to use YouTube debug
- `YOUTUBE_DEBUG_TROUBLESHOOTING.md` - Fix connection issues
- `DEPLOY_NOW.md` - Deployment guide

---

**Last Updated:** 2025-11-20  
**Maintained by:** AI Assistant

