# 🌐 Production-Only Deployment

**This project is configured for PRODUCTION DEPLOYMENT ONLY.**

Local development is disabled to avoid confusion and errors.

---

## 🚀 Live URLs

### **Frontend (Vercel)**
```
https://your-project.vercel.app
```

### **Backend (Railway)**
```
https://salesbestfriend-production.up.railway.app
```

---

## 📦 Deployment Flow

### **Every Git Push Triggers:**

1. **Railway** auto-deploys backend (2-3 minutes)
2. **Vercel** auto-deploys frontend (1-2 minutes)

```bash
git add -A
git commit -m "Your changes"
git push origin main
```

**That's it!** ✅

---

## 🔍 Check Deployment Status

### **Railway Backend:**
```bash
curl https://salesbestfriend-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "coach_connections": 0,
  "is_live_recording": false
}
```

### **Vercel Frontend:**
Open in browser: `https://your-project.vercel.app`

---

## 🐛 Debugging

### **View Railway Logs:**
1. Open: https://railway.app/project/your-project
2. Click on deployment
3. View live logs

### **View Vercel Logs:**
1. Open: https://vercel.com/dashboard
2. Click on project
3. View deployment logs

---

## ⚠️ Local Development Disabled

**Files disabled:**
- ❌ `LOCAL_start_backend.sh.disabled`
- ❌ `LOCAL_start_frontend.sh.disabled`
- ❌ `LOCAL_START_HERE.md.disabled`

**Why?**
- Avoids confusion between local and production
- Ensures testing on actual production environment
- Prevents CORS and environment variable issues

---

## 🔧 Configuration

### **Backend (Railway):**
- Environment variables set in Railway dashboard
- Dockerfile builds automatically
- Port: 8000 (internal)

### **Frontend (Vercel):**
- Environment variables in `vercel.json`:
  - `VITE_API_WS`: `wss://salesbestfriend-production.up.railway.app`
  - `VITE_API_HTTP`: `https://salesbestfriend-production.up.railway.app`

---

## 📚 Documentation

- `API_DOCUMENTATION.md` - Complete API reference
- `YOUTUBE_STREAMING_MODE.md` - YouTube debug explanation
- `DEPLOY_NOW.md` - Deployment guide
- `PRODUCT_ARCHITECTURE.md` - System architecture

---

## ✅ Quick Test

### **1. Open Frontend:**
```
https://your-project.vercel.app
```

### **2. Test YouTube Debug:**
- Click "🎬 YouTube Debug"
- Paste: `https://www.youtube.com/watch?v=NikP6phDVgw`
- Click "🔍 Analyze Video"
- Open DevTools (F12) to see logs

### **3. Check Backend Response:**
```bash
curl -X POST https://salesbestfriend-production.up.railway.app/api/process-youtube \
  -F "url=https://www.youtube.com/watch?v=test" \
  -F "language=id" \
  -F "real_time=false"
```

---

## 🎯 Summary

**Development Flow:**
```
Edit code → Commit → Push → Auto-deploy → Test on Production URLs
```

**No local servers needed!** ✅

---

**Last Updated:** 2025-11-20  
**Status:** Production-Only Mode Active

