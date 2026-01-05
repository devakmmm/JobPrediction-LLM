# Quick Start Guide

This guide will get you up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm

## Step 1: Setup Environment

```bash
# Run the setup script
bash scripts/setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

## Step 2: Train a Model (Optional but Recommended)

Train a model on the sample data:

```bash
python ml/train.py \
  --csv data/processed/software_engineer_new_york,ny.csv \
  --role "Software Engineer" \
  --location "New York, NY" \
  --window 12 \
  --epochs 50
```

This creates model artifacts in `backend/app/artifacts/software_engineer_new_york,ny/`.

**Note**: The API endpoints require trained models. If you skip this step, the `/forecast` endpoint will return 404 errors.

## Step 3: Start Backend

```bash
# Make sure venv is activated
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

Backend will be available at `http://localhost:8000`

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Step 4: Start Frontend

Open a new terminal:

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Step 5: Use the Dashboard

1. Open `http://localhost:3000` in your browser
2. Select a role (e.g., "Software Engineer")
3. Select a location (e.g., "New York, NY")
4. Click "Generate Forecast"

You should see:
- Historical data (blue line)
- Forecasted values (red dashed line)
- Optional baseline comparison (green dashed line)

## Troubleshooting

### "No trained model found" error

This means you need to train a model first. Run Step 2 above.

### API not responding

- Check that the backend is running on port 8000
- Check that the frontend is configured to connect to `http://localhost:8000`

### Port already in use

- Backend: Change port with `uvicorn backend.app.main:app --reload --port 8001`
- Frontend: Update `vite.config.js` port or `VITE_API_BASE` in `.env.local`

## Next Steps

- Train models for other roles/locations
- Fetch fresh data from USAJOBS API (see README.md)
- Customize the LSTM architecture in `ml/models.py`
- Add more baseline models in `ml/baselines.py`

## Testing

Run tests:

```bash
pytest tests/
```

Check API health:

```bash
curl http://localhost:8000/health
```
