# Deployment Guide - Render (Free Tier)

## Quick Overview

**Render** is excellent for this app because:
- ✅ Free tier for both backend (Web Service) and frontend (Static Site)
- ✅ Built-in Python support (FastAPI backend)
- ✅ Automatic HTTPS
- ✅ Environment variables support
- ✅ Auto-deploy from Git
- ✅ No credit card required for free tier

**Free Tier Limits:**
- Backend: 750 hours/month (enough for 24/7 if it's your only service)
- Frontend: Unlimited (static sites)
- 512 MB RAM, 0.1 CPU
- Auto-sleeps after 15 min inactivity (wakes on request)

## Deployment Steps

### 1. Prepare Repository

Ensure your code is in a Git repository (GitHub, GitLab, or Bitbucket).

### 2. Deploy Backend (FastAPI)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `job-market-forecaster-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: (leave empty)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

5. Add Environment Variables (if needed):
   - `PYTHON_VERSION`: `3.12.0`
   - `PORT`: `10000` (Render sets this automatically, but good to have)

6. Click "Create Web Service"
7. Wait for build (3-5 minutes first time)
8. Copy the URL: `https://your-app.onrender.com`

### 3. Deploy Frontend (React)

1. In Render Dashboard, click "New +" → "Static Site"
2. Connect your repository
3. Configure:
   - **Name**: `job-market-forecaster-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Plan**: `Free`

4. Add Environment Variable:
   - `VITE_API_BASE`: `https://your-backend-url.onrender.com` (from step 2)

5. Click "Create Static Site"
6. Wait for build
7. Copy the URL: `https://your-frontend.onrender.com`

### 4. Update Frontend API URL

After deploying, update the frontend environment variable to point to your backend URL.

**Option A: Use Render Environment Variables**
- In frontend static site settings, set: `VITE_API_BASE=https://your-backend.onrender.com`
- Rebuild the site

**Option B: Update frontend/src/api.js**
```javascript
const API_BASE = import.meta.env.VITE_API_BASE || 'https://your-backend.onrender.com';
```

### 5. CORS Configuration

Update `backend/app/main.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.onrender.com",  # Add your Render frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Alternative: Deploy Both in One Service (Simpler)

You can serve the frontend from the FastAPI backend:

1. Build frontend: `cd frontend && npm run build`
2. Update `backend/app/main.py`:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add after creating app
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('frontend/dist/index.html')

# Keep your API routes as-is
```

3. Deploy only the backend service
4. Point frontend build to the backend URL

## Prevent Service from Sleeping (Keep-Alive Setup)

Render's free tier sleeps after 15 minutes. **See `scripts/keep_alive_instructions.md` for detailed setup.**

**Quick Setup (GitHub Actions - Recommended):**
1. Add secret to GitHub: `RENDER_URL=https://your-backend.onrender.com`
2. The `.github/workflows/keep-alive.yml` workflow will auto-ping every 10 minutes
3. This keeps your service awake 24/7 on free tier!

**Alternative: UptimeRobot (Free):**
- Sign up at uptimerobot.com
- Add monitor: `https://your-backend.onrender.com/health`
- Set interval: 5 minutes
- Done!

## Optimizations for Free Tier

1. **Reduce Model Size**: Use CPU-only PyTorch builds
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

2. **Enable Caching**: Models load on first request (cold start ~30s)

3. **Health Check**: Use `/health` or `/ping` endpoint with external pinger
   - See `scripts/keep_alive_instructions.md` for setup

4. **Consider Model Storage**: 
   - Free tier has limited disk
   - For large models, use external storage (AWS S3, Cloudflare R2 free tier)

## Testing Deployment

1. Backend health: `curl https://your-backend.onrender.com/health`
2. Frontend: Visit `https://your-frontend.onrender.com`
3. Test forecast endpoint from frontend

## Troubleshooting

**Cold Starts**: First request after sleep takes ~30s. Subsequent requests are fast.

**Build Failures**: 
- Check build logs in Render dashboard
- Ensure `requirements.txt` is in root
- Verify Python version matches

**CORS Errors**:
- Add frontend URL to `allow_origins` in backend
- Check browser console for exact error

**Model Loading Issues**:
- Ensure model artifacts are committed (or use external storage)
- Check file paths are relative

## Other Free Options

**Railway** (Free tier, requires card):
- Similar to Render
- Better free tier (more resources)
- Requires credit card (but free plan available)

**Fly.io** (Free tier):
- Good for Python apps
- Global edge network
- 3 shared VMs free

**Vercel** (Free tier):
- Great for frontend
- Backend via serverless functions (limited for ML)

**Netlify** (Free tier):
- Similar to Vercel
- Good for static sites

## Recommendation

**Render is the best free option** for this full-stack ML app because:
- No credit card needed
- Simple deployment
- Good Python support
- Separate backend/frontend services
- Automatic HTTPS

The only downside is the 15-minute sleep timer on free tier, but it's fine for demos/portfolios.
