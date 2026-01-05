# Render Deployment Guide - Step by Step

Complete guide to deploy your Job Market Demand Forecaster to Render (free tier).

## Prerequisites

✅ Your code is pushed to GitHub (already done: https://github.com/devakmmm/JobPrediction-LLM)
✅ You have a Render account (sign up at https://render.com - free, no credit card needed)
✅ You've trained at least one model (or will use the pre-trained artifacts)

## Part 1: Deploy Backend (FastAPI)

### Step 1: Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### Step 2: Connect Repository

1. Click **"Connect account"** or **"Connect GitHub"**
2. Authorize Render to access your GitHub account
3. Find and select: **`devakmmm/JobPrediction-LLM`**
4. Click **"Connect"**

### Step 3: Configure Backend Service

Fill in these settings:

**Basic Settings:**
- **Name**: `job-market-forecaster-backend` (or any name you like)
- **Region**: Choose closest to you (Oregon, Frankfurt, Singapore)
- **Branch**: `main` (or your default branch name)
- **Root Directory**: (leave empty - this uses the repository root)
  
  ⚠️ **Important**: Leave empty because:
  - `requirements.txt` is in the root directory
  - Start command uses `backend.app.main` which is relative to root
  - Python imports expect root as working directory

- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Select **"Free"**

### Step 4: Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add:

- **Key**: `PYTHON_VERSION`
- **Value**: `3.12.0`

(Note: `$PORT` is automatically set by Render, no need to add it)

### Step 5: Health Check

1. Scroll down to **"Health Check Path"**
2. Enter: `/health`
3. This enables Render's health monitoring

### Step 6: Create Service

1. Click **"Create Web Service"**
2. Render will start building (takes 3-5 minutes first time)
3. Wait for build to complete - you'll see logs streaming

### Step 7: Get Your Backend URL

Once deployed, Render gives you a URL like:
- `https://job-market-forecaster-backend-xxxx.onrender.com`

**Copy this URL** - you'll need it for the frontend!

---

## Part 2: Deploy Frontend (React)

### Step 1: Create New Static Site

1. In Render Dashboard, click **"New +"**
2. Select **"Static Site"**

### Step 2: Connect Repository

1. Select the same repository: **`devakmmm/JobPrediction-LLM`**
2. Click **"Connect"**

### Step 3: Configure Frontend

Fill in these settings:

**Basic Settings:**
- **Name**: `job-market-forecaster-frontend`
- **Branch**: `main`
- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`

**Plan:**
- Select **"Free"**

### Step 4: Environment Variables

Click **"Add Environment Variable"**:

- **Key**: `VITE_API_BASE`
- **Value**: Your backend URL from Part 1 (e.g., `https://job-market-forecaster-backend-xxxx.onrender.com`)

**Important:** Make sure there's NO trailing slash!

### Step 5: Create Static Site

1. Click **"Create Static Site"**
2. Wait for build (takes 2-3 minutes)
3. Get your frontend URL

---

## Part 3: Update CORS Settings

After deployment, update backend CORS to allow your frontend:

### Option A: Update Code (Recommended)

1. Edit `backend/app/main.py`
2. Find the `cors_origins` list (around line 28)
3. Add your frontend URL:
   ```python
   cors_origins = [
       "http://localhost:3000",
       "http://localhost:5173",
       "http://localhost:5174",
       "https://your-frontend.onrender.com",  # Add this
   ]
   ```
4. Commit and push:
   ```bash
   git add backend/app/main.py
   git commit -m "Add Render frontend URL to CORS"
   git push origin main
   ```
5. Render will auto-deploy (takes ~2 minutes)

### Option B: Allow All Origins (Quick Test)

Temporarily allow all origins for testing:
```python
cors_origins = ["*"]  # Only for testing!
```

---

## Part 4: Model Artifacts & Data Files

Your trained models and data need to be in the repository for Render to access them.

### Check What's Committed

Run this locally to see what's tracked:
```bash
git ls-files | grep -E "(artifacts|processed)"
```

### If Models Are Missing

If you haven't trained models yet or they're not in the repo:

1. **Train a model locally:**
   ```bash
   python ml/train.py \
     --csv data/processed/software_engineer_new_york,ny.csv \
     --role "Software Engineer" \
     --location "New York, NY" \
     --window 12 \
     --epochs 20
   ```

2. **Commit the artifacts:**
   ```bash
   git add backend/app/artifacts/
   git commit -m "Add trained model artifacts"
   git push origin main
   ```

3. **Render will auto-deploy** with the new artifacts

### File Size Limits

- Render free tier: ~100MB disk space
- If models are too large:
  - Use external storage (AWS S3, Cloudflare R2 free tier)
  - Or optimize model size (quantization, smaller architecture)

---

## Part 5: Testing Deployment

### Test Backend

1. **Health Check:**
   ```bash
   curl https://your-backend.onrender.com/health
   ```
   Should return: `{"ok":true}`

2. **Ping Endpoint:**
   ```bash
   curl https://your-backend.onrender.com/ping
   ```
   Should return timestamp

3. **Forecast Endpoint:**
   ```bash
   curl "https://your-backend.onrender.com/forecast?role=Software%20Engineer&location=New%20York,%20NY&horizon=8"
   ```
   Should return JSON with forecast data

### Test Frontend

1. Visit your frontend URL: `https://your-frontend.onrender.com`
2. Check browser console (F12) for errors
3. Try generating a forecast
4. Verify data loads correctly

---

## Part 6: Troubleshooting

### Backend Issues

**Build Fails:**
- Check build logs in Render dashboard
- Verify `requirements.txt` is in root directory
- Check Python version matches (3.12.0)

**Import Errors:**
- Make sure all dependencies are in `requirements.txt`
- Check that paths are relative (not absolute)
- Verify `PYTHONPATH` or sys.path setup

**Model Not Found Errors:**
- Check that artifacts are committed to git
- Verify path: `backend/app/artifacts/software_engineer_new_york_ny/`
- Check file names: `model.pt`, `scaler.pkl`, `metadata.json`

**CORS Errors:**
- Add frontend URL to `cors_origins` in `main.py`
- Check browser console for exact error
- Verify backend URL is correct in frontend env var

### Frontend Issues

**Build Fails:**
- Check build logs
- Verify `package.json` exists in `frontend/` directory
- Check Node.js version (Render uses Node 18+)

**API Connection Errors:**
- Verify `VITE_API_BASE` env var is set correctly
- Check network tab in browser DevTools
- Verify backend is running (check Render dashboard)

**Blank Page:**
- Check browser console for errors
- Verify build completed successfully
- Check that `dist/` folder exists after build

### Cold Start Issues

**First Request Takes 30+ Seconds:**
- Normal for Render free tier (service sleeps after 15 min)
- Set up GitHub Actions keep-alive (see GITHUB_ACTIONS_SETUP.md)
- Or accept the cold start delay

**Service Keeps Sleeping:**
- Free tier auto-sleeps after 15 min inactivity
- Set up external pinger (GitHub Actions, UptimeRobot)
- Consider paid tier for always-on service

### Common Fixes

**Clear Build Cache:**
1. Go to Render service → Settings
2. Click "Clear build cache"
3. Manual deploy → Deploy latest commit

**Check Logs:**
1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. Look for errors/warnings

**Redeploy:**
1. Go to Render dashboard
2. Click your service
3. Click "Manual Deploy" → "Deploy latest commit"

---

## Part 7: Verify Everything Works

### Checklist

- [ ] Backend deploys successfully
- [ ] Backend health check works (`/health`)
- [ ] Frontend builds successfully
- [ ] Frontend loads without errors
- [ ] API calls work (check browser Network tab)
- [ ] Forecasts generate correctly
- [ ] CORS is configured (no CORS errors in console)
- [ ] Models load (no "model not found" errors)

### Quick Test Script

Run this to test all endpoints:

```bash
# Set your backend URL
BACKEND_URL="https://your-backend.onrender.com"

echo "Testing health..."
curl "$BACKEND_URL/health"

echo -e "\n\nTesting ping..."
curl "$BACKEND_URL/ping"

echo -e "\n\nTesting forecast..."
curl "$BACKEND_URL/forecast?role=Software%20Engineer&location=New%20York,%20NY&horizon=8"
```

---

## Part 8: Next Steps

After successful deployment:

1. **Set up keep-alive** (prevent sleep):
   - See `GITHUB_ACTIONS_SETUP.md`
   - Add `RENDER_URL` secret to GitHub
   - Workflow will auto-ping every 10 minutes

2. **Monitor your app:**
   - Check Render dashboard for service status
   - Monitor logs for errors
   - Set up alerts (Render dashboard → Settings)

3. **Optimize:**
   - Train models for other role/location combinations
   - Add more features to dashboard
   - Set up custom domain (paid tier)

---

## Quick Reference

**Backend URL Format:**
```
https://your-service-name.onrender.com
```

**Frontend URL Format:**
```
https://your-site-name.onrender.com
```

**Important Files:**
- `requirements.txt` - Python dependencies
- `backend/app/main.py` - FastAPI app
- `frontend/package.json` - Node dependencies
- `render.yaml` - Render config (optional)

**Key Endpoints:**
- `/health` - Health check
- `/ping` - Keep-alive ping
- `/forecast` - Get forecast
- `/series` - Get historical data

---

## Need Help?

If you get stuck:
1. Check Render build/deployment logs
2. Check browser console (F12) for frontend errors
3. Verify all environment variables are set
4. Make sure all files are committed to git
5. Try clearing build cache and redeploying

Good luck! 🚀
