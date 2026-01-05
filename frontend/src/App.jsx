import React, { useState, useEffect } from 'react';
import ForecastChart from './components/ForecastChart';
import ProjectExplanation from './components/ProjectExplanation';
import { getForecast, checkHealth } from './api';
import './App.css';

const COUNT_FORMATTER = new Intl.NumberFormat('en-US', { maximumFractionDigits: 1 });
const PERCENT_FORMATTER = new Intl.NumberFormat('en-US', { maximumFractionDigits: 1, signDisplay: 'always' });

const formatCount = (value) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'n/a';
  }
  return COUNT_FORMATTER.format(value);
};

const formatPercent = (value) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'n/a';
  }
  return `${PERCENT_FORMATTER.format(value)}%`;
};

const formatDate = (value) => {
  if (!value) {
    return 'n/a';
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }
  return parsed.toLocaleDateString('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric'
  });
};

const average = (values) => {
  if (!values.length) {
    return null;
  }
  const sum = values.reduce((total, value) => total + value, 0);
  return sum / values.length;
};

const standardDeviation = (values) => {
  if (values.length < 2) {
    return null;
  }
  const mean = average(values);
  const variance = values.reduce((total, value) => total + (value - mean) ** 2, 0) / values.length;
  return Math.sqrt(variance);
};

// Sample roles and locations
const SAMPLE_ROLES = [
  'Software Engineer',
  'Data Scientist',
  'Product Manager'
];

const SAMPLE_LOCATIONS = [
  'New York, NY',
  'San Francisco, CA',
  'Remote'
];

function App() {
  const [role, setRole] = useState(SAMPLE_ROLES[0]);
  const [location, setLocation] = useState(SAMPLE_LOCATIONS[0]);
  // Default to 52 weeks for Software Engineer + New York, NY (June 2025 to June 2026)
  const [horizon, setHorizon] = useState(52);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showBaseline, setShowBaseline] = useState(false);
  const [apiHealth, setApiHealth] = useState(null);

  // Check API health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setApiHealth(true))
      .catch(() => setApiHealth(false));
  }, []);

  const handleForecast = async () => {
    if (loading) return; // Prevent duplicate requests
    
    setLoading(true);
    setError(null);

    try {
      console.log('Fetching forecast for:', { role, location, horizon });
      const data = await getForecast(role, location, horizon);
      console.log('Forecast data received:', data);
      setForecastData(data);
      setError(null); // Clear any previous errors
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch forecast';
      console.error('Forecast error:', err);
      setError(errorMessage);
      setForecastData(null); // Clear data on error
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch on mount
  useEffect(() => {
    handleForecast();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  const history = forecastData?.history ?? [];
  const forecast = forecastData?.forecast ?? [];
  const model = forecastData?.model ?? {};
  const historyValues = history.map((point) => point.value);

  const latestPoint = history[history.length - 1];
  const latestValue = latestPoint ? latestPoint.value : null;
  const latestDate = latestPoint ? latestPoint.week_start : null;

  const recentAverage = average(history.slice(-12).map((point) => point.value));
  const historyMin = historyValues.length ? Math.min(...historyValues) : null;
  const historyMax = historyValues.length ? Math.max(...historyValues) : null;
  const volatility = standardDeviation(historyValues);

  const historySpan = history.length
    ? `${formatDate(history[0].week_start)} to ${formatDate(history[history.length - 1].week_start)}`
    : 'n/a';

  const forecastSpan = forecast.length
    ? `${formatDate(forecast[0].week_start)} to ${formatDate(forecast[forecast.length - 1].week_start)}`
    : 'n/a';

  const forecastStart = forecast[0];
  const forecastEnd = forecast[forecast.length - 1];
  const forecastDelta = forecastStart && forecastEnd ? forecastEnd.value - forecastStart.value : null;
  const forecastDeltaPct = forecastDelta !== null && forecastStart?.value
    ? (forecastDelta / forecastStart.value) * 100
    : null;
  const trendLabel = forecastDeltaPct === null
    ? 'n/a'
    : forecastDeltaPct > 3
      ? 'Uptrend'
      : forecastDeltaPct < -3
        ? 'Downtrend'
        : 'Stable';
  const trendClass = trendLabel === 'Uptrend'
    ? 'trend-up'
    : trendLabel === 'Downtrend'
      ? 'trend-down'
      : 'trend-flat';

  const modelType = model.type ? model.type.toUpperCase() : 'LSTM';
  const modelWindow = model.window ? `${model.window} weeks` : 'n/a';
  const trainedOn = formatDate(model.trained_on);

  const forecastWeeks = forecast.length ? forecast.length : horizon;
  const historyRangeLabel = historyMin !== null && historyMax !== null
    ? `${formatCount(historyMin)} to ${formatCount(historyMax)}`
    : 'n/a';
  const forecastTrendDetail = forecastDeltaPct !== null
    ? `${formatPercent(forecastDeltaPct)} projected change`
    : 'n/a';

  const apiStatusClass = apiHealth === null ? 'pending' : apiHealth ? 'online' : 'offline';
  const apiStatusLabel = apiHealth === null ? 'Checking' : apiHealth ? 'Online' : 'Offline';
  const telemetryStatus = loading ? 'Updating' : 'Live';

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-grid">
          <div className="header-title">
            <div className="header-eyebrow">Demand Intelligence Console</div>
            <h1>Job Market Demand Forecaster</h1>
            <p className="subtitle">Predict weekly job postings volume with LSTM time series modeling.</p>
          </div>
          <div className="header-meta">
            <div className="meta-card">
              <span className="meta-label">Model</span>
              <span className="meta-value">{modelType}</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">Window</span>
              <span className="meta-value">{modelWindow}</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">API</span>
              <span className={`meta-status ${apiStatusClass}`}>
                <span className="status-dot" />
                {apiStatusLabel}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="app-main">
        <section className="overview-panel">
          <div className="overview-header">
            <div>
              <h2>Signal Overview</h2>
              <p>Live summary of demand signals and forecast posture.</p>
            </div>
            <div className="overview-chips">
              <span className="overview-chip">Role: {role}</span>
              <span className="overview-chip">Location: {location}</span>
              <span className="overview-chip">Horizon: {horizon} weeks</span>
            </div>
          </div>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-label">Latest weekly volume</span>
              <span className="stat-value">{formatCount(latestValue)}</span>
              <span className="stat-sub">as of {formatDate(latestDate)}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">12 week average</span>
              <span className="stat-value">{formatCount(recentAverage)}</span>
              <span className="stat-sub">rolling mean</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Forecast trend</span>
              <span className={`stat-value ${trendClass}`}>{trendLabel}</span>
              <span className="stat-sub">{forecastTrendDetail}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Forecast horizon</span>
              <span className="stat-value">{forecastWeeks} weeks</span>
              <span className="stat-sub">{forecastSpan}</span>
            </div>
          </div>
        </section>

        <div className="dashboard-grid">
          <div className="controls">
            <div className="panel-header">
              <div>
                <h3>Query Controls</h3>
                <p>Choose the target role, market, and horizon.</p>
              </div>
              <span className={`panel-chip ${loading ? 'busy' : ''}`}>{loading ? 'Busy' : 'Ready'}</span>
            </div>
            <div className="control-grid">
              <div className="control-group">
                <label htmlFor="role">Job role</label>
                <select
                  id="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  disabled={loading}
                >
                  {SAMPLE_ROLES.map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              <div className="control-group">
                <label htmlFor="location">Location</label>
                <select
                  id="location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  disabled={loading}
                >
                  {SAMPLE_LOCATIONS.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>

              <div className="control-group">
                <label htmlFor="horizon">Forecast horizon (weeks)</label>
                <input
                  id="horizon"
                  type="number"
                  min="1"
                  max="52"
                  value={horizon}
                  onChange={(e) => setHorizon(parseInt(e.target.value) || 8)}
                  disabled={loading}
                />
              </div>

              <div className="control-group">
                <label htmlFor="baseline-toggle">Baseline overlay</label>
                <div className="toggle-row">
                  <input
                    id="baseline-toggle"
                    type="checkbox"
                    checked={showBaseline}
                    onChange={(e) => setShowBaseline(e.target.checked)}
                    disabled={loading}
                  />
                  <span>Enable naive baseline</span>
                </div>
              </div>
            </div>

            <div className="control-actions">
              <button
                onClick={handleForecast}
                disabled={loading}
                className="forecast-button"
              >
                {loading ? 'Loading...' : 'Generate Forecast'}
              </button>
            </div>
          </div>

          <div className="telemetry-panel">
            <div className="panel-header">
              <div>
                <h3>Model Telemetry</h3>
                <p>Data coverage and runtime notes.</p>
              </div>
              <span className="panel-chip">{telemetryStatus}</span>
            </div>
            <div className="telemetry-grid">
              <div className="telemetry-item">
                <span className="telemetry-label">Data source</span>
                <span className="telemetry-value">USAJOBS weekly</span>
                <span className="telemetry-sub">federal listings feed</span>
              </div>
              <div className="telemetry-item">
                <span className="telemetry-label">History coverage</span>
                <span className="telemetry-value">{history.length ? `${history.length} weeks` : 'n/a'}</span>
                <span className="telemetry-sub">{historySpan}</span>
              </div>
              <div className="telemetry-item">
                <span className="telemetry-label">History range</span>
                <span className="telemetry-value">{historyRangeLabel}</span>
                <span className="telemetry-sub">min to max volume</span>
              </div>
              <div className="telemetry-item">
                <span className="telemetry-label">Volatility</span>
                <span className="telemetry-value">{formatCount(volatility)}</span>
                <span className="telemetry-sub">std dev</span>
              </div>
              <div className="telemetry-item">
                <span className="telemetry-label">Model window</span>
                <span className="telemetry-value">{modelWindow}</span>
                <span className="telemetry-sub">input sequence length</span>
              </div>
              <div className="telemetry-item">
                <span className="telemetry-label">Model trained</span>
                <span className="telemetry-value">{trainedOn}</span>
                <span className="telemetry-sub">last training time</span>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
            <br />
            <small>
              Make sure the backend is running: <code>uvicorn backend.app.main:app --reload</code>
            </small>
          </div>
        )}

        <ProjectExplanation role={role} location={location} />

        {forecastData && (
          <div className="chart-container">
            <div className="chart-header">
              <h2>
                {forecastData.role} - {forecastData.location}
              </h2>
              <div className="model-info">
                <small>
                  Model: {forecastData.model.type.toUpperCase()} (Window: {forecastData.model.window} weeks)
                </small>
              </div>
            </div>
            <ForecastChart data={forecastData} showBaseline={showBaseline} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Built with PyTorch LSTM, FastAPI, and React
        </p>
      </footer>
    </div>
  );
}

export default App;
