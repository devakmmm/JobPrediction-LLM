# Job Market Demand Forecaster

A complete ML-powered application that forecasts weekly job postings volume using LSTM neural networks. Built with PyTorch for training, FastAPI for serving, and React for visualization.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Quick Start (Offline)](#quick-start-offline)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Data Leakage Prevention](#data-leakage-prevention)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ForecastChart.jsx  │  App.jsx  │  api.js           │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↕ HTTP/REST                          │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  main.py  │  forecast.py  │  data_store.py          │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↕                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Load Model Artifacts (model.pt, scaler.pkl)        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              ML Training Pipeline (PyTorch)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  train.py → models.py → datasets.py → export.py     │   │
│  │  baselines.py → evaluate.py                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↕                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Processed CSV → Sliding Windows → LSTM Training    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      Data Pipeline                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  fetch_usajobs.py → data/raw/                       │   │
│  │  process.py → data/processed/                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

- **LSTM-based Forecasting**: Deep learning model for time series prediction
- **Baseline Comparisons**: Naive, Moving Average, and optional ARIMA baselines
- **RESTful API**: FastAPI backend with automatic documentation
- **Interactive Dashboard**: React frontend with Recharts visualization
- **Data Leakage Prevention**: Proper train/val/test splits with scaler fitting on train only
- **Deterministic Runs**: Reproducible training with fixed seeds
- **Offline Capable**: Sample data included for testing without API access

## 🚀 Quick Start (Offline)

The repository includes sample processed data and can work offline. To get started quickly:

### 1. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Install ML dependencies (if not included)
pip install torch scikit-learn matplotlib pandas numpy

# Start backend server
cd ..
uvicorn backend.app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Train a Model (Optional)

If you want to train a model from the sample data:

```bash
python ml/train.py \
  --csv data/processed/software_engineer_new_york,ny.csv \
  --role "Software Engineer" \
  --location "New York, NY" \
  --window 12 \
  --epochs 50
```

This will:
- Train an LSTM model
- Evaluate against baselines
- Generate forecast plots
- Export model artifacts to `backend/app/artifacts/`

### 4. View Results

- Open `http://localhost:3000` in your browser
- Select a role and location from the dropdowns
- Click "Generate Forecast" to see predictions

## 📦 Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- (Optional) USAJOBS API credentials for live data fetching

### Backend Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   pip install torch scikit-learn matplotlib statsmodels  # ML dependencies
   ```

3. **Set environment variables (optional, for USAJOBS API):**
   ```bash
   export USAJOBS_API_KEY="your-api-key"
   export USAJOBS_USER_AGENT="your-email@example.com"
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API endpoint (optional):**
   Create `frontend/.env.local`:
   ```
   VITE_API_BASE=http://localhost:8000
   ```

## 📊 Usage

### Data Ingestion

#### Option 1: Use Sample Data (Offline)

Sample processed CSV files are included in `data/processed/`:
- `software_engineer_new_york,ny.csv`
- `data_scientist_san_francisco,ca.csv`
- `product_manager_remote.csv`

#### Option 2: Fetch from USAJOBS API

1. **Fetch raw data:**
   ```bash
   python data/fetch_usajobs.py \
     --keyword "Software Engineer" \
     --location "New York, NY" \
     --date-from "2022-01-01" \
     --date-to "2024-12-31" \
     --output data/raw/software_engineer_nyc.json
   ```

2. **Process to weekly aggregates:**
   ```bash
   python data/process.py \
     --input data/raw/software_engineer_nyc.json \
     --role "Software Engineer" \
     --location "New York, NY" \
     --output data/processed/software_engineer_new_york,ny.csv
   ```

### Model Training

Train an LSTM model:

```bash
python ml/train.py \
  --csv data/processed/software_engineer_new_york,ny.csv \
  --role "Software Engineer" \
  --location "New York, NY" \
  --window 12 \
  --hidden-size 64 \
  --num-layers 2 \
  --epochs 50 \
  --batch-size 32 \
  --learning-rate 0.001
```

**Arguments:**
- `--csv`: Path to processed CSV file
- `--role`: Job role name
- `--location`: Location name
- `--window`: Window size for LSTM (default: 12)
- `--hidden-size`: LSTM hidden units (default: 64)
- `--num-layers`: Number of LSTM layers (default: 2)
- `--epochs`: Training epochs (default: 50)
- `--batch-size`: Batch size (default: 32)
- `--learning-rate`: Learning rate (default: 0.001)

**Outputs:**
- Model artifacts in `backend/app/artifacts/<role_slug>_<location_slug>/`
- Metrics in `reports/metrics.json`
- Forecast plot in `reports/forecast_plot.png`

### Running the Application

1. **Start backend:**
   ```bash
   uvicorn backend.app.main:app --reload
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access dashboard:**
   Open `http://localhost:3000`

## 🔒 Data Leakage Prevention

The implementation follows strict practices to prevent data leakage:

### 1. **Chronological Splitting**
- Train/val/test splits are done **chronologically** (no shuffling)
- This preserves the temporal nature of time series data

### 2. **Scaler Fitting**
- Scaler is fitted **only on training data**
- Same scaler is then applied to validation and test sets
- This prevents future information from leaking into training

### 3. **Window-Based Sequences**
- Each training sample uses only past data (no future lookahead)
- Sliding windows ensure no overlap between train/val/test sequences

### 4. **No Information Leakage in Training**
- Model never sees test data during training
- Early stopping uses only validation loss
- Metrics are computed separately for each split

**Implementation details:**

```python
# In ml/datasets.py
def prepare_datasets(train_df, val_df, test_df, ...):
    # Fit scaler ONLY on training data
    scaler.fit(train_values)
    
    # Apply same scaler to all splits
    train_scaled = scaler.transform(train_values)
    val_scaled = scaler.transform(val_values)  # Using train's parameters
    test_scaled = scaler.transform(test_values)  # Using train's parameters
```

## 📁 Project Structure

```
.
├── data/
│   ├── raw/                    # Cached USAJOBS API responses
│   ├── processed/              # Weekly aggregated CSV files
│   ├── fetch_usajobs.py        # API fetching script
│   └── process.py              # Data processing script
├── ml/
│   ├── train.py                # End-to-end training script
│   ├── models.py               # LSTM model definition
│   ├── datasets.py             # Time series dataset utilities
│   ├── baselines.py            # Baseline models
│   ├── evaluate.py             # Metrics and visualization
│   └── export.py               # Model artifact export
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   ├── schemas.py          # Pydantic models
│   │   ├── config.py           # Configuration
│   │   ├── services/
│   │   │   ├── forecast.py     # Forecast service
│   │   │   └── data_store.py   # Data access service
│   │   └── artifacts/          # Trained model artifacts
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── components/
│   │   │   └── ForecastChart.jsx
│   │   ├── api.js              # API client
│   │   └── App.css
│   ├── package.json
│   └── vite.config.js
├── reports/                    # Training metrics and plots
├── tests/                      # Unit tests
└── README.md
```

## 📡 API Documentation

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "ok": true
}
```

#### `GET /series`
Get historical time series data.

**Query Parameters:**
- `role` (required): Job role name
- `location` (required): Location name
- `max_weeks` (optional): Maximum weeks to return (default: 104)

**Response:**
```json
{
  "role": "Software Engineer",
  "location": "New York, NY",
  "series": [
    {
      "week_start": "2022-01-03",
      "value": 45.0
    },
    ...
  ]
}
```

#### `GET /forecast`
Generate forecast for a role/location.

**Query Parameters:**
- `role` (required): Job role name
- `location` (required): Location name
- `horizon` (optional): Forecast horizon in weeks (1-52, default: 8)

**Response:**
```json
{
  "role": "Software Engineer",
  "location": "New York, NY",
  "history": [
    {
      "week_start": "2022-01-03",
      "value": 45.0
    },
    ...
  ],
  "forecast": [
    {
      "week_start": "2024-12-30",
      "value": 279.0
    },
    ...
  ],
  "model": {
    "type": "lstm",
    "window": 12,
    "trained_on": "2024-01-15T10:30:00"
  }
}
```

**Interactive API docs:** Visit `http://localhost:8000/docs` when the server is running.

## 🧪 Testing

Run tests:

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_datasets.py -v

# Run with coverage
pytest --cov=ml --cov=backend tests/
```

## 📝 Notes

- **USAJOBS API**: Requires free API key from [USAJOBS](https://developer.usajobs.gov/)
- **Deterministic Training**: Set `torch.manual_seed()` for reproducibility
- **Model Artifacts**: Models are saved with metadata including training date range and metrics
- **Recursive Forecasting**: Multi-step forecasts use recursive prediction (1-step model applied repeatedly)

## 🤝 Contributing

This is a complete, runnable project. To extend:

1. Add new baseline models in `ml/baselines.py`
2. Modify LSTM architecture in `ml/models.py`
3. Add new API endpoints in `backend/app/main.py`
4. Extend frontend components in `frontend/src/`

## 📄 License

This project is provided as-is for educational and demonstration purposes.
