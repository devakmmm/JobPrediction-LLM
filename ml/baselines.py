"""
Baseline forecasting models for comparison:
- Naive persistence (last value)
- Moving average
- Optional ARIMA (if statsmodels available)
"""
import numpy as np
from typing import Optional
import warnings


class NaiveBaseline:
    """Naive persistence: predict the last observed value."""
    
    def __init__(self):
        self.last_value = None
    
    def fit(self, train_data: np.ndarray):
        """Fit: store the last value."""
        self.last_value = train_data[-1] if len(train_data) > 0 else 0.0
    
    def predict(self, horizon: int) -> np.ndarray:
        """Predict: repeat last value for horizon steps."""
        if self.last_value is None:
            raise ValueError("Model must be fitted before prediction")
        return np.full(horizon, self.last_value)


class MovingAverageBaseline:
    """Moving average: predict the mean of the last k values."""
    
    def __init__(self, window: int = 4):
        """
        Initialize moving average baseline.
        
        Args:
            window: Number of recent values to average
        """
        self.window = window
        self.mean_value = None
    
    def fit(self, train_data: np.ndarray):
        """Fit: compute mean of last window values."""
        if len(train_data) < self.window:
            self.mean_value = np.mean(train_data) if len(train_data) > 0 else 0.0
        else:
            self.mean_value = np.mean(train_data[-self.window:])
    
    def predict(self, horizon: int) -> np.ndarray:
        """Predict: repeat mean value for horizon steps."""
        if self.mean_value is None:
            raise ValueError("Model must be fitted before prediction")
        return np.full(horizon, self.mean_value)


class ARIMABaseline:
    """ARIMA baseline (optional, requires statsmodels)."""
    
    def __init__(self, order: tuple = (1, 1, 1)):
        """
        Initialize ARIMA baseline.
        
        Args:
            order: (p, d, q) ARIMA order
        """
        self.order = order
        self.model = None
        self.fitted_model = None
        self.fallback_value = 0.0
        self.is_available = False
        
        # Try to import statsmodels
        try:
            from statsmodels.tsa.arima.model import ARIMA
            self.ARIMA = ARIMA
            self.is_available = True
        except ImportError:
            warnings.warn(
                "statsmodels not available. ARIMA baseline will be skipped. "
                "Install with: pip install statsmodels"
            )
    
    def fit(self, train_data: np.ndarray):
        """Fit ARIMA model."""
        if not self.is_available:
            raise RuntimeError("statsmodels not installed. Cannot use ARIMA baseline.")
        
        try:
            self.model = self.ARIMA(train_data, order=self.order)
            self.fitted_model = self.model.fit()
        except Exception as e:
            warnings.warn(f"ARIMA fitting failed: {e}. Using naive fallback.")
            self.fitted_model = None
            self.fallback_value = train_data[-1] if len(train_data) > 0 else 0.0
    
    def predict(self, horizon: int) -> np.ndarray:
        """Predict using ARIMA."""
        if not self.is_available:
            raise RuntimeError("statsmodels not installed.")
        
        if self.fitted_model is None:
            # Fallback to naive if fitting failed
            return np.full(horizon, self.fallback_value)
        
        try:
            forecast = self.fitted_model.forecast(steps=horizon)
            return forecast.values if hasattr(forecast, 'values') else forecast
        except Exception as e:
            warnings.warn(f"ARIMA prediction failed: {e}. Using naive fallback.")
            return np.full(horizon, self.fallback_value)


def compute_baseline_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> dict:
    """
    Compute evaluation metrics for baseline predictions.
    
    Returns:
        Dictionary with RMSE, MAPE, and directional accuracy
    """
    # Remove zeros/very small values for MAPE
    mask = np.abs(y_true) > 1e-6
    
    # RMSE
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    # MAPE (only where true values are non-zero)
    if mask.sum() > 0:
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        mape = np.nan
    
    # Directional accuracy (sign of change)
    if len(y_true) > 1:
        true_deltas = np.diff(y_true) > 0
        pred_deltas = np.diff(y_pred) > 0
        directional_acc = np.mean(true_deltas == pred_deltas) * 100
    else:
        directional_acc = np.nan
    
    return {
        "rmse": float(rmse),
        "mape": float(mape),
        "directional_accuracy": float(directional_acc)
    }
