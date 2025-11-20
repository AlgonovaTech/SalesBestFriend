# 🚀 Sales Best Friend - Production Deployment

**Real-time AI Sales Assistant for Zoom Trial Classes**

---

## 🌐 Live Application

### **👉 Open App:** https://sales-best-friend-tkoj.vercel.app/

### **Backend API:** https://salesbestfriend-production.up.railway.app/

---

## 🎯 Features

- ✅ **Real-time transcription** (Bahasa Indonesia)
- ✅ **Checklist tracking** (7 stages, 29 items)
- ✅ **Client info extraction** (AI-powered)
- ✅ **Time-based coaching** (stage timing)
- ✅ **YouTube Debug Mode** (test with recorded calls)
- ✅ **Visual Config Editor** (customize call structure)

---

## 🎬 Quick Test: YouTube Debug

1. **Open:** https://sales-best-friend-tkoj.vercel.app/
2. **Click:** "🎬 YouTube Debug" button
3. **Paste URL:** `https://www.youtube.com/watch?v=NikP6phDVgw`
4. **Open DevTools:** Press F12 (console tab)
5. **Click:** "🔍 Analyze Video"
6. **Wait:** 3-5 minutes for processing

**Expected output:**
```
✅ Analysis complete!
Transcript: 5432 chars
Stage: discovery
Completed: 12/29 items
Client info: 8 fields filled
```

---

## 🛠️ Tech Stack

### **Frontend (Vercel)**
- React + TypeScript
- Vite
- WebSocket for real-time updates
- Notion-inspired UI design

### **Backend (Railway)**
- FastAPI (Python)
- Faster Whisper (transcription)
- Claude 3.5 Haiku via OpenRouter (LLM analysis)
- WebSocket for streaming
- Docker deployment

---

## 📊 Architecture

```
┌─────────────────────────┐
│  Vercel Frontend        │
│  (React + TypeScript)   │
└──────────┬──────────────┘
           │
           │ WebSocket + HTTP
           │
┌──────────▼──────────────┐
│  Railway Backend        │
│  (FastAPI + Whisper)    │
├─────────────────────────┤
│  • /ingest (audio)      │
│  • /coach (updates)     │
│  • /api/process-youtube │
└──────────┬──────────────┘
           │
           │ API calls
           │
┌──────────▼──────────────┐
│  OpenRouter             │
│  (Claude 3.5 Haiku)     │
└─────────────────────────┘
```

---

## 🔧 Configuration

### **Call Structure:**
- 7 stages (Greeting → Close)
- 29 checklist items
- Time budgets per stage
- Editable via Settings UI

### **Client Card:**
- 11 structured fields
- Grouped by category
- AI auto-fill from conversation
- Read-only display

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `API_DOCUMENTATION.md` | Complete API reference |
| `YOUTUBE_STREAMING_MODE.md` | How YouTube debug works |
| `PRODUCT_ARCHITECTURE.md` | System architecture |
| `PRODUCTION_ONLY.md` | Deployment guide |

---

## 🚀 Deployment

### **Automatic Deployment:**
```bash
git add -A
git commit -m "Your changes"
git push origin main
```

**Result:**
- Railway rebuilds backend (2-3 min)
- Vercel rebuilds frontend (1-2 min)

### **Check Deployment:**
```bash
# Backend health
curl https://salesbestfriend-production.up.railway.app/health

# Frontend
open https://sales-best-friend-tkoj.vercel.app/
```

---

## 🐛 Debugging

### **View Logs:**

**Railway (Backend):**
1. https://railway.app/project/your-project
2. Click deployment
3. View logs

**Vercel (Frontend):**
1. https://vercel.com/dashboard
2. Click project
3. View deployment logs

### **Common Issues:**

**CORS Error:**
- ✅ Fixed! CORS enabled on backend

**YouTube Processing Slow:**
- ⏱️ Real-time mode simulates live call (20 min video = 20 min processing)
- ⚡ Use `real_time=false` for fast processing (3-5 min)

**WebSocket Connection Failed:**
- Check Railway backend is running
- Verify `VITE_API_WS` env variable

---

## 🎓 Usage Guide

### **1. Live Recording Mode**
- Connect microphone
- Click "🎤 Start Recording"
- Share screen with Zoom audio
- Watch real-time analysis

### **2. YouTube Debug Mode**
- Click "🎬 YouTube Debug"
- Paste recorded call URL
- Simulates real-time processing
- Test without live call

### **3. Settings Editor**
- Click "⚙️ Settings"
- Edit call structure (stages/items)
- Edit client fields (categories/fields)
- Export/Import JSON config

---

## 📈 System Status

✅ **Frontend:** Online  
✅ **Backend:** Online  
✅ **Transcription:** Ready  
✅ **LLM Analysis:** Ready  
✅ **YouTube Debug:** Ready  
✅ **CORS:** Enabled  

---

## 📞 Support

**Issues?**
- Check `YOUTUBE_DEBUG_TROUBLESHOOTING.md`
- View Railway/Vercel logs
- Check backend health endpoint

---

## 🎯 Version

**Current:** v2.0.0  
**Last Update:** 2025-11-20  
**Mode:** Production-Only  

---

**Live URL:** https://sales-best-friend-tkoj.vercel.app/

**Happy Coaching!** 🎉

