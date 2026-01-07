# GitHub Actions Keep-Alive Setup

This guide shows you how to set up GitHub Actions to automatically ping your Render service every 10 minutes, preventing it from going idle.

## Step-by-Step Setup

### Step 1: Get Your Render Backend URL

1. Deploy your backend to Render (if not already done)
2. Copy your backend URL, e.g., `https://your-app.onrender.com`
3. You'll need this URL in Step 2

### Step 2: Add GitHub Secret

1. Go to your GitHub repository: `https://github.com/devakmmm/JobPrediction-LLM`
2. Click on **Settings** (top menu bar of your repo)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the **New repository secret** button
5. Fill in:
   - **Name**: `RENDER_URL`
   - **Secret**: Paste your Render backend URL (e.g., `https://your-app.onrender.com`)
6. Click **Add secret**

✅ The secret is now saved and can be used by GitHub Actions workflows.

### Step 3: Verify the Workflow File

The workflow file is already created at `.github/workflows/keep-alive.yml`. Let's verify it exists:

**File location:** `.github/workflows/keep-alive.yml`

The workflow:
- Runs every 10 minutes automatically
- Pings your Render service at `/health` endpoint
- Uses the `RENDER_URL` secret you just created

### Step 4: Enable GitHub Actions (if needed)

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. If this is your first workflow, you may need to click **"I understand my workflows, go ahead and enable them"**
4. The workflow will automatically start running

### Step 5: Verify It's Working

1. Go to the **Actions** tab in your GitHub repo
2. You should see "Keep Render Service Alive" in the workflows list
3. Click on it to see the workflow runs
4. You should see runs happening every ~10 minutes
5. Green checkmark ✅ = successful ping
6. Red X ❌ = ping failed (check the URL/secret)

### Step 6: Check Logs

To see if it's actually pinging:

1. Click on a workflow run in the Actions tab
2. Click on the **"Ping Render Service"** job
3. You should see output like:
   ```
   $ curl -f "https://your-app.onrender.com/health"
   {"ok":true}
   ```

## Customizing the Workflow

If you want to change the ping interval or URL, edit `.github/workflows/keep-alive.yml`:

```yaml
on:
  schedule:
    - cron: '*/10 * * * *'  # Change this: */10 = every 10 minutes
                            # */5 = every 5 minutes
                            # */15 = every 15 minutes
```

**Cron syntax:**
- `*/5 * * * *` = Every 5 minutes
- `*/10 * * * *` = Every 10 minutes (recommended)
- `*/15 * * * *` = Every 15 minutes (too slow - service might sleep)

## Troubleshooting

### Workflow not running?
- Check that GitHub Actions is enabled in repository Settings → Actions
- Verify the workflow file is in `.github/workflows/` directory
- Check that you've pushed the file to the `main` branch

### Getting 404 errors?
- Verify your `RENDER_URL` secret is correct
- Make sure your Render service is deployed and running
- Check that the `/health` endpoint exists on your backend

### Workflow shows "Failed"?
- Check the workflow logs for the exact error
- Verify the `RENDER_URL` secret is set correctly
- Test the URL manually: `curl https://your-app.onrender.com/health`

### Service still sleeping?
- Make sure the workflow is running successfully (green checkmarks)
- Check Render logs to see if pings are arriving
- Consider using a shorter interval (every 5 minutes) or add UptimeRobot as backup

## Alternative: Manual Testing

You can manually trigger the workflow:

1. Go to **Actions** tab
2. Click **"Keep Render Service Alive"** workflow
3. Click **"Run workflow"** button (top right)
4. Select branch: `main`
5. Click **"Run workflow"**
6. This will immediately ping your service (useful for testing)

## How It Works

1. **GitHub Actions** runs the workflow every 10 minutes (cron schedule)
2. The workflow uses `curl` to ping your Render backend at `/health`
3. This keeps the service "active" so Render doesn't put it to sleep
4. Free tier services sleep after 15 minutes of inactivity
5. By pinging every 10 minutes, the service stays awake 24/7

## Cost

✅ **GitHub Actions is FREE** for public repositories and includes:
- 2,000 minutes/month for private repos
- Unlimited minutes for public repos

This workflow uses ~4 minutes/month (6 pings/hour × 24 hours × 30 days × 10 seconds per ping), so it's well within free limits!

## Status

Once set up, you should see:
- ✅ Workflow running every 10 minutes
- ✅ Green checkmarks in Actions tab
- ✅ Render service stays awake (no 30-second cold starts)
- ✅ Your app is available 24/7 on free tier!
