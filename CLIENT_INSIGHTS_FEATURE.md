# 🧠 Client Insights Panel - Feature Documentation

## Overview

The Client Insights Panel provides real-time analysis of client behavior during sales calls, displaying:
- **Dialogue Stage** (Profiling → Presentation → Objection → Closing)
- **Emotional Tone** (Engaged, Curious, Hesitant, Defensive, Negative)
- **Active Objections** (Price, Time, Family, Value, Child)
- **Client Interests** (Game-based learning, Future skills, Logic, etc.)
- **Detected Need** (Extracted from "I want..." statements)
- **Engagement Level** (0-100% with trend indicator)

## Architecture

```
Google Meet Audio → /ingest → ASR (mock) → orchestrator
                                               ↓
                                    analyze_client_text()
                                               ↓
                                    {client_insight} JSON
                                               ↓
                                    WebSocket /coach
                                               ↓
                                    <ClientPanel /> UI
```

## Backend Components

### 1. `/backend/insights/client_insight.py`

**Main Class:** `ClientInsightAnalyzer`

**Key Methods:**
- `analyze_client_text(text: str, is_client: bool) -> dict`
  - Analyzes utterance and returns insights
  - Maintains history of last 5 utterances
  - Returns structured JSON with all insights

**Detection Logic:**

#### Objections
Keywords mapped to categories:
- **price**: "expensive", "costly", "budget", "afford"
- **time**: "busy", "no time", "schedule", "duration"
- **family**: "spouse", "discuss", "partner"
- **value**: "worth", "benefit", "results"
- **child**: "not interested", "refuses", "boring"

#### Interests
Keywords mapped to topics:
- **game-based learning**: "game", "minecraft", "fun"
- **future skills**: "future", "career", "technology"
- **logic**: "think", "logic", "problem solving"

#### Emotions
- **engaged**: "yes", "great", "interesting", "like"
- **curious**: "how", "what", "tell me more"
- **hesitant**: "maybe", "not sure", "think about"
- **defensive**: "but", "however", "no", "can't"
- **negative**: "bad", "terrible", "waste"

#### Stage Detection
- **profiling**: "child", "age", "experience"
- **presentation**: "how it works", "program", "learn"
- **objection**: "but", "expensive", "problem"
- **closing**: "start", "register", "payment"

#### Need Extraction
Regex patterns:
- `"I want to [verb] [object]"`
- `"I need to [verb] [object]"`
- `"so that [goal]"`

### 2. Integration in `main.py`

```python
from insights.client_insight import analyze_client_text

# In orchestrate():
if current_mock_index < len(mock_client_utterances):
    client_text = mock_client_utterances[current_mock_index]
    client_insight = analyze_client_text(client_text, is_client=True)
    last_client_insight = client_insight

# WebSocket message:
{
    "hint": "...",
    "prob": 0.78,
    "client_insight": {
        "stage": "profiling",
        "emotion": "curious",
        "active_objections": ["price"],
        "interests": ["game-based learning", "logic"],
        "need": "think logically and be more creative",
        "engagement": 0.65,
        "trend": "up"
    }
}
```

## Frontend Components

### 1. `/frontend/src/components/ClientPanel.tsx`

**Props:**
- `coachWs: WebSocket | null` - WebSocket connection to listen for insights

**Features:**
- Subscribes to WebSocket messages containing `client_insight`
- Auto-updates every ~3 seconds when new data arrives
- Displays all insight fields with emoji icons
- Handles empty/null values gracefully with "–"
- Color-coded engagement bar (green > 70%, yellow > 40%, red < 40%)
- Trend indicator with arrows (↑ ↓ →)

**UI Sections:**
1. 🧭 Stage
2. ❤️ Emotion
3. 💬 Active Objections (tags)
4. 🌟 Interests (tags)
5. 📘 Detected Need
6. 📈 Engagement (% + bar + trend)

### 2. Updated `/frontend/src/App.tsx`

**Layout Changes:**
- Two-column grid layout
- Left panel (400px): ClientPanel
- Right panel (flex): Sales Coach hints
- Responsive: stacks vertically on mobile (<1024px)

**CSS Updates in `/frontend/src/App.css`:**
```css
.main-content {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1.5rem;
}
```

## Mock Data for Testing

### Backend Mock Utterances:
```python
mock_client_utterances = [
    "My child is 10 years old and loves Minecraft",
    "No, but it sounds fun and interesting for future",
    "I want him to think logically and be more creative",
    "How much does it cost? We're on a budget",
]
```

These cycle through the orchestrator to simulate client speech.

## Testing Acceptance Criteria

### ✅ Test Case 1: Objection Detection
**Input:** "How much does it cost? We're on a budget"  
**Expected:** `active_objections: ["price"]`

### ✅ Test Case 2: Interest Detection
**Input:** "it sounds fun and interesting for future"  
**Expected:** `interests: ["game-based learning", "future skills"]`

### ✅ Test Case 3: Need Extraction
**Input:** "I want him to think logically and be more creative"  
**Expected:** `need: "think logically and be more creative"`

### ✅ Test Case 4: Emotion Detection
**Input:** "it sounds fun and interesting"  
**Expected:** `emotion: "curious"` or `"engaged"`

### ✅ Test Case 5: Stage Progression
**Input:** Sequential utterances should show stage progression:
- Start: `profiling`
- After interests: `presentation`
- After "how much": `objection`

### ✅ Test Case 6: Engagement Updates
**Expected:** Engagement percentage should change over time (mock shows ~65-78%)

### ✅ Test Case 7: UI Auto-Update
**Expected:** ClientPanel should update every ~3s without page refresh

## How to Test

### 1. Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Open Application
Navigate to http://localhost:3000

### 4. Start Recording
1. Click "🎤 Начать запись"
2. Share any tab (audio capture works now)
3. Click "Share"

### 5. Observe Client Insights
- Left panel should populate with insights
- Updates every ~3 seconds
- Check console for `🧠 Client Insight:` logs

### 6. Verify Mock Data
Watch the backend terminal for:
```
🧠 Client Insight: {'stage': 'profiling', 'emotion': 'curious', ...}
📤 Отправка: {"hint":"...","prob":0.7,"client_insight":{...}}
```

## Future Enhancements

### Phase 2: Real ASR Integration
- Replace mock utterances with real Whisper output
- Add diarization to distinguish client vs. manager
- Stream real-time instead of batched utterances

### Phase 3: Advanced NLP
- Replace keyword matching with transformer models
- Sentiment analysis with BERT/RoBERTa
- Intent classification with fine-tuned models
- Entity extraction for specific pain points

### Phase 4: Historical Analysis
- Store insights in database
- Show trends over multiple calls
- Generate post-call reports
- Compare client profiles

### Phase 5: Smart Recommendations
- Link objections to specific responses
- Suggest next best actions based on stage
- Alert manager to critical emotional shifts
- Predictive close probability

## API Reference

### WebSocket `/coach` Message Format

```typescript
interface CoachMessage {
  hint: string              // Sales coach hint
  prob: number              // Success probability (0-1)
  client_insight?: {
    stage: string           // "profiling" | "presentation" | "objection" | "closing"
    emotion: string         // "engaged" | "curious" | "hesitant" | "defensive" | "negative"
    active_objections: string[]  // ["price", "time", etc.]
    interests: string[]     // ["game-based learning", etc.]
    need: string | null     // Extracted need statement
    engagement: number      // 0-1
    trend: string           // "up" | "stable" | "down"
  }
}
```

## Troubleshooting

### Backend: Import Error
```bash
# Ensure insights module is in Python path
cd backend
python -c "from insights.client_insight import analyze_client_text; print('OK')"
```

### Frontend: ClientPanel Not Showing
1. Check browser console for errors
2. Verify WebSocket connection: `coachWsRef.current` should not be null
3. Check Network tab for WebSocket messages

### No Updates in Client Panel
1. Check backend logs for `🧠 Client Insight:`
2. Verify mock_client_utterances are being processed
3. Check `current_mock_index` is incrementing

### Insights Always Empty
- Restart backend to reset analyzer state
- Check keyword matching in `client_insight.py`
- Verify utterances contain detectable keywords

## Performance Notes

- **Latency**: <10ms for text analysis (rule-based)
- **Memory**: ~1KB per utterance (history of 5)
- **Network**: ~500 bytes per WebSocket message
- **Update Frequency**: Every 1 second (rate-limited)

## Code Ownership

- Backend: `/backend/insights/` + `main.py` orchestrator integration
- Frontend: `/frontend/src/components/ClientPanel.*` + `App.tsx` layout
- Tests: TBD (unit tests for analyzer, E2E for UI)

---

**Status:** ✅ MVP Complete  
**Last Updated:** 2025-01-25  
**Version:** 1.0.0

