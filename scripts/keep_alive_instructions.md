# Keep Render Service Alive - Setup Guide

Render's free tier puts services to sleep after 15 minutes of inactivity. Here are several ways to keep your service awake:

## Option 1: GitHub Actions (Recommended - Free & Automatic)

1. **Set up GitHub Secret:**
   - Go to your repo: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `RENDER_URL`
   - Value: `https://your-backend.onrender.com`
   - Click "Add secret"

2. **Enable GitHub Actions:**
   - The workflow file `.github/workflows/keep-alive.yml` is already created
   - Update the `RENDER_URL` in the workflow file OR use the secret (recommended)
   - Commit and push to GitHub
   - GitHub Actions will automatically run every 10 minutes

3. **Verify it's working:**
   - Go to your repo: Actions tab
   - You should see "Keep Render Service Alive" running every 10 minutes
   - Green checkmarks = service is being pinged successfully

## Option 2: UptimeRobot (Free - 50 monitors)

1. Go to [UptimeRobot.com](https://uptimerobot.com) and sign up (free)
2. Click "Add New Monitor"
3. Configure:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: Render Keep-Alive
   - **URL**: `https://your-backend.onrender.com/health`
   - **Monitoring Interval**: 5 minutes
4. Click "Create Monitor"
5. UptimeRobot will ping your service every 5 minutes (free tier limit)

## Option 3: Python Script (Local Machine)

If you have a machine that's always on (or use it when you're working):

1. **Install dependencies:**
   ```bash
   pip install requests
   ```

2. **Run the script:**
   ```bash
   export RENDER_URL=https://your-backend.onrender.com
   python scripts/keep_alive.py
   ```

3. **Set up a cron job (Linux/Mac):**
   ```bash
   # Edit crontab
   crontab -e
   
   # Add this line (runs every 10 minutes):
   */10 * * * * cd /path/to/project && /usr/bin/python3 scripts/keep_alive.py >> /tmp/render_ping.log 2>&1
   ```

4. **Windows Task Scheduler:**
   - Create a new task
   - Trigger: Every 10 minutes
   - Action: Run `python scripts/keep_alive.py`
   - Set environment variable `RENDER_URL`

## Option 4: Multiple Free Services

Use several services together for redundancy:

- **UptimeRobot**: Every 5 minutes
- **GitHub Actions**: Every 10 minutes  
- **Cronitor.io**: Free tier (5 monitors)
- **StatusCake**: Free tier (10 monitors)

## Option 5: Render's Health Check (Doesn't Prevent Sleep)

Render has a built-in health check, but it only restarts failed services - it doesn't prevent sleep.

To enable:
1. In Render dashboard → Your service → Settings
2. Add Health Check Path: `/health`
3. Save

This helps with reliability but won't keep the service awake.

## Recommended Setup

**Best combination for free:**
1. **GitHub Actions** (every 10 min) - automatic, reliable
2. **UptimeRobot** (every 5 min) - backup, external monitoring
3. **Render Health Check** - for automatic restarts if service fails

This ensures your service stays awake 24/7 on Render's free tier!

## Troubleshooting

**Service still sleeping?**
- Check that pings are actually reaching the service
- Verify the URL is correct
- Make sure GitHub Actions or UptimeRobot shows successful pings
- Check Render logs to see if requests are arriving

**Cold start delays?**
- First request after sleep takes ~30 seconds
- Subsequent requests are fast
- This is normal for Render's free tier
