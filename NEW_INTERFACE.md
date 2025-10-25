# 🎨 New Interface - Sales Coach Dashboard

## Overview

The interface has been completely redesigned to provide a comprehensive sales coaching experience with real-time guidance, client insights, and progress tracking.

---

## 🎯 Interface Structure (Top to Bottom)

### 1. **Next Step Recommendation Card** (Top)
**Purpose:** Provides actionable guidance for the next step in the sales call

**Features:**
- Current call stage badge (Greeting, Discovery, Presentation, Objections, Closing)
- Live update indicator
- AI-generated recommendation based on:
  - Current stage of the call
  - Checklist progress
  - Client insights
  - Best practices

**Updates:** Every 15 seconds (or on new transcript)

**Example:**
```
┌─────────────────────────────────────────┐
│ 🔍 Discovery                     ● Live│
│                                         │
│ Next Step Recommendation                │
│                                         │
│ 💡 Ask open-ended questions about      │
│    pain points                          │
└─────────────────────────────────────────┘
```

---

### 2. **Key Client Information Summary**
**Purpose:** Track important information gathered from the client

**Displays:**
- **Objections** (⚠️): Price concerns, time constraints, etc.
- **Interests** (⭐): Topics that caught client's attention
- **Needs** (🎯): Client's stated goals and requirements
- **Emotion** (😊): Current emotional state (engaged, curious, hesitant, etc.)
- **Engagement** (%): Percentage of client engagement

**Max:** 10 items displayed

**Example:**
```
┌─────────────────────────────────────────┐
│ Key Client Information           4 items│
├─────────────────────────────────────────┤
│ ⚠️ Objections                           │
│  • price                                │
│  • time                                 │
│                                         │
│ ⭐ Interests                            │
│  • game-based learning                  │
│                                         │
│ 😊 Emotion: curious                     │
│ ████████░░ 80% engaged                  │
└─────────────────────────────────────────┘
```

---

### 3. **Call Progress Checklist**
**Purpose:** Track progress through sales call best practices

**Structure:**
Based on proven sales methodology, divided into 5 stages:

#### **Stage 1: Greeting & Rapport** 👋
- [ ] Introduce yourself and company
- [ ] Check if they have time for the call
- [ ] Set agenda and expectations
- [ ] Build initial rapport (small talk)

#### **Stage 2: Discovery & Profiling** 🔍
- [ ] Understand current situation
- [ ] Identify pain points and challenges
- [ ] Discover goals and desired outcomes
- [ ] Understand decision-making process
- [ ] Qualify budget and timeline
- [ ] Identify all stakeholders

#### **Stage 3: Solution Presentation** 📊
- [ ] Tailor solution to their needs
- [ ] Demo key features relevant to pain points
- [ ] Show clear value and ROI
- [ ] Provide case studies/examples
- [ ] Check understanding and engagement

#### **Stage 4: Objection Handling** 💬
- [ ] Address price concerns
- [ ] Address time/implementation concerns
- [ ] Differentiate from competitors
- [ ] Address perceived risks
- [ ] Confirm objection is resolved

#### **Stage 5: Closing & Next Steps** 🤝
- [ ] Summarize key benefits and fit
- [ ] Ask for commitment or next step
- [ ] Schedule specific follow-up action
- [ ] Confirm materials to send
- [ ] Thank them for their time

**Features:**
- **Active stage highlighted** (blue border + Active badge)
- **Completed items** get checkmarks ✓
- **Progress bars** for each stage
- **Total progress** ring at top
- **Auto-detection:** System analyzes transcript and auto-checks items

**Example:**
```
┌─────────────────────────────────────────┐
│ Call Progress Checklist         15/25   │
│                                    60%   │
├─────────────────────────────────────────┤
│ 👋 Greeting & Rapport  ████████  3/4    │
│  ✓ Introduce yourself and company       │
│  ✓ Check if they have time              │
│  ✓ Set agenda                           │
│  □ Build rapport                        │
│                                         │
│ 🔍 Discovery [Active]  ████░░░░  2/6    │
│  ✓ Understand current situation         │
│  ✓ Identify pain points                 │
│  □ Discover goals                       │
│  ...                                    │
└─────────────────────────────────────────┘
```

---

### 4. **Deal Success Probability**
**Purpose:** Show likelihood of closing the deal

**Displays:**
- Large percentage number
- Colored progress bar:
  - 🟢 Green (>70%): High probability
  - 🟠 Orange (40-70%): Medium probability
  - 🔴 Red (<40%): Low probability

**Updates:** Every 1 second based on LLM analysis

---

### 5. **Debug & Input Modes** (Bottom)
**Purpose:** Developer tools and alternative input methods

**Modes:**
- **🎤 Live** - Real-time audio capture from browser tab
- **📝 Text** - Paste transcript directly
- **📺 Video** - Upload video file (coming soon)
- **🔗 YouTube** - Process YouTube video URL

**Controls:**
- "🎤 Start Live Recording" / "⏹️ Stop Recording" button
- Instructions for audio capture

---

## 🔄 Data Flow

```
Audio Input (Live/YouTube/Text)
           ↓
    Transcription
           ↓
    ┌──────┴──────┐
    ↓             ↓
Stage Detection  Checklist Tracking
    ↓             ↓
    └──────┬──────┘
           ↓
   Client Insight Analysis
           ↓
   LLM Analysis (Claude)
           ↓
   Next Step Generation
           ↓
   WebSocket Broadcast
           ↓
   UI Update (All Components)
```

---

## 🎨 Design Features

### Color Scheme
- **Purple Gradient** - Next Step Card (premium, actionable)
- **White Cards** - Information display (clean, professional)
- **Blue Highlight** - Active stage (focus)
- **Green** - Success, completion, high probability
- **Orange** - Warning, medium states
- **Red** - Objections, low probability

### Typography
- **Bold, Large** - Important metrics and headers
- **Regular** - Body text
- **Icons** - Visual recognition (emoji-based)

### Animations
- **Pulse** - Live indicators
- **Smooth transitions** - Progress bars, stage changes
- **Fade in** - New information

---

## 📱 Responsive Design

### Desktop (>768px)
- Multi-column layout for checklist stages
- Full width cards
- All features visible

### Mobile (<768px)
- Single column layout
- Stacked cards
- Collapsible sections
- Full-width buttons

---

## 🔧 Technical Implementation

### Frontend Components

1. **NextStepCard.tsx** - Top recommendation display
   - Props: `coachWs` (WebSocket)
   - Listens to: `next_step`, `current_stage`

2. **ClientInfoSummary.tsx** - Client information panel
   - Props: `coachWs` (WebSocket)
   - Listens to: `client_insight`

3. **CallChecklist.tsx** - Progress checklist
   - Props: `coachWs` (WebSocket)
   - Listens to: `current_stage`, `checklist_progress`

4. **DebugPanel.tsx** - Input modes (existing)

### Backend Modules

1. **sales_checklist.py** - Checklist logic
   - `detect_stage_from_text()` - NLP-based stage detection
   - `check_checklist_item()` - Keyword-based item detection
   - `generate_next_step_recommendation()` - Context-aware guidance

2. **main.py** - WebSocket & orchestration
   - Tracks: `current_stage`, `checklist_progress`, `accumulated_transcript`
   - Broadcasts: Full state to all connected clients

### WebSocket Message Format

```json
{
  "hint": "Уточните у клиента опыт ребёнка...",
  "prob": 0.75,
  "client_insight": {
    "stage": "discovery",
    "emotion": "curious",
    "active_objections": ["price"],
    "interests": ["game-based learning"],
    "need": "logical thinking",
    "engagement": 0.8,
    "trend": "up"
  },
  "next_step": "📍 Discover goals: Ask open-ended questions about pain points",
  "current_stage": "discovery",
  "checklist_progress": {
    "intro_yourself": true,
    "ask_availability": true,
    "set_agenda": false,
    ...
  }
}
```

---

## 🚀 How to Use

### For Sales Managers

1. **Start a call** (Google Meet, Zoom, or upload recording)
2. **Click "Start Live Recording"** and select the tab
3. **Watch the interface:**
   - Follow **Next Step** recommendations
   - Monitor **Client Insights** for objections/interests
   - Track **Checklist** progress
   - Adjust approach based on **Probability**

### For Developers

1. **Backend updates:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend updates:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test with different inputs:**
   - Live mode for real-time
   - Text mode for quick testing
   - YouTube mode for recorded calls

---

## 📊 Checklist Source

The checklist is based on industry best practices for B2C EdTech/SaaS sales calls, incorporating:
- SPIN Selling methodology
- Challenger Sale techniques
- Solution Selling framework
- Consultative selling best practices

**Customization:**
To modify the checklist, edit `/backend/sales_checklist.py` → `SALES_CHECKLIST` dictionary.

---

## 🎯 Key Benefits

1. **Real-time guidance** - Never miss a crucial step
2. **Objective tracking** - See progress vs. best practices
3. **Client insights** - Track objections and interests automatically
4. **Stage awareness** - Know where you are in the conversation
5. **Data-driven** - Probability score based on actual performance

---

## 🐛 Troubleshooting

### Checklist not updating
- Check browser console for WebSocket messages
- Verify `checklist_progress` in message payload
- Ensure transcript contains relevant keywords

### Stage detection incorrect
- System uses keyword-based NLP
- Accumulates last 500 words of transcript
- May need 10-20 seconds to stabilize

### Next Step not relevant
- Recommendation based on:
  - Current uncompleted checklist items
  - Overall stage progress
  - Client insights
- Improves as call progresses

---

## 🎨 Future Enhancements

- [ ] Custom checklist templates per product/industry
- [ ] Historical call analysis & comparison
- [ ] Team performance dashboard
- [ ] Voice sentiment analysis
- [ ] Live translation for multilingual calls
- [ ] Integration with CRM systems

---

**Built with ❤️ for sales professionals**

