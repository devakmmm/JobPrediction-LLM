# Deployment Configuration Guide

Quick reference for what URLs/credentials go where.

## Backend URL Configuration

You need the **backend URL** in **TWO places**:

### 1. Frontend Environment Variable (Required)

**Purpose**: So your React frontend knows where to send API requests.

**Where**: Render Dashboard → Frontend Static Site → Environment Variables

**Setting:**
- **Key**: `VITE_API_BASE`
- **Value**: `https://your-backend-name.onrender.com`
- **Important**: No trailing slash!

**Example:**
```
VITE_API_BASE=https://job-market-forecaster-backend-xxxx.onrender.com
```

**Why**: The frontend needs this to make API calls to your backend.

---

### 2. GitHub Actions Secret (Optional but Recommended)

**Purpose**: To ping your backend every 10 minutes to prevent it from sleeping.

**Where**: GitHub Repository → Settings → Secrets and variables → Actions

**Setting:**
- **Secret Name**: `RENDER_URL`
- **Secret Value**: `https://your-backend-name.onrender.com`
- **Important**: Same URL as above (backend URL, not frontend)

**Example:**
```
RENDER_URL=https://job-market-forecaster-backend-xxxx.onrender.com
```

**Why**: Keeps your backend service awake 24/7 on Render's free tier.

---

## Frontend URL Configuration

You need the **frontend URL** in **ONE place**:

### Backend CORS Settings (Required)

**Purpose**: Allow your frontend to make API requests (CORS).

**Where**: `backend/app/main.py`

**Setting:**
```python
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-frontend-name.onrender.com",  # Add your Render frontend URL
]
```

**Or** (if using the auto-detection code):
- The code already detects Render and allows all origins
- But it's better to be explicit for security

---

## Quick Setup Checklist

After deploying to Render:

1. ✅ **Get Backend URL** from Render dashboard
   - Example: `https://job-market-forecaster-backend-xxxx.onrender.com`

2. ✅ **Add to Frontend** (Render Dashboard):
   - Environment Variable: `VITE_API_BASE` = backend URL

3. ✅ **Add to GitHub Actions** (GitHub Settings):
   - Secret: `RENDER_URL` = backend URL

4. ✅ **Get Frontend URL** from Render dashboard
   - Example: `https://job-market-forecaster-frontend-xxxx.onrender.com`

5. ✅ **Update Backend CORS** (optional, but recommended):
   - Edit `backend/app/main.py`
   - Add frontend URL to `cors_origins`
   - Commit and push

---

## URL Summary

| Service | Where Used | Purpose |
|---------|-----------|---------|
| **Backend URL** | Frontend env var (`VITE_API_BASE`) | Frontend makes API calls |
| **Backend URL** | GitHub Actions secret (`RENDER_URL`) | Keep-alive pings |
| **Frontend URL** | Backend CORS settings | Allow API requests |

---

## Example Values

If your Render services are:
- Backend: `https://job-market-forecaster-backend-abc123.onrender.com`
- Frontend: `https://job-market-forecaster-frontend-xyz789.onrender.com`

**Then configure:**

**Frontend Environment Variable:**
```
VITE_API_BASE=https://job-market-forecaster-backend-abc123.onrender.com
```

**GitHub Actions Secret:**
```
RENDER_URL=https://job-market-forecaster-backend-abc123.onrender.com
```

**Backend CORS (in main.py):**
```python
cors_origins = [
    "http://localhost:3000",
    "https://job-market-forecaster-frontend-xyz789.onrender.com",
]
```

---

## Testing

After configuration:

1. **Test Backend:**
   ```bash
   curl https://your-backend.onrender.com/health
   ```

2. **Test Frontend:**
   - Visit frontend URL
   - Open browser console (F12)
   - Check Network tab for API calls
   - Should see requests to backend URL

3. **Test Keep-Alive:**
   - Go to GitHub Actions tab
   - Check "Keep Render Service Alive" workflow
   - Should show successful pings every 10 minutes
