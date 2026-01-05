"""
Model evaluation utilities: metrics and visualization.
"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Tuple
import json
import torch


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute evaluation metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
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


def plot_forecasts(
    train_values: np.ndarray,
    val_values: np.ndarray,
    test_values: np.ndarray,
    test_predictions: np.ndarray,
    baseline_predictions: Dict[str, np.ndarray],
    scaler: object,
    save_path: Path,
    title: str = "Forecast Comparison"
):
    """
    Plot historical data and forecasts.
    
    Args:
        train_values: Training values (raw scale)
        val_values: Validation values (raw scale)
        test_values: Test values (raw scale)
        test_predictions: LSTM predictions (scaled, will be inverse transformed)
        baseline_predictions: Dict of baseline name -> predictions (scaled)
        scaler: Scaler to inverse transform
        save_path: Path to save plot
        title: Plot title
    """
    # Inverse transform predictions
    test_pred_inv = scaler.inverse_transform(test_predictions.reshape(-1, 1)).flatten()
    
    baseline_preds_inv = {}
    for name, pred in baseline_predictions.items():
        baseline_preds_inv[name] = scaler.inverse_transform(
            pred.reshape(-1, 1)
        ).flatten()
    
    # Prepare data for plotting
    train_len = len(train_values)
    val_len = len(val_values)
    test_len = len(test_values)
    
    # Predictions are shorter because we need window_size values to make a prediction
    # So we only predict for test_len - window_size + 1 points, but we need to align with test_values
    # For now, assume test_predictions corresponds to the last len(test_predictions) values of test
    pred_len = len(test_predictions)
    test_values_for_pred = test_values[-pred_len:] if pred_len < test_len else test_values
    
    # Create time indices
    train_idx = np.arange(train_len)
    val_idx = np.arange(train_len, train_len + val_len)
    # Test indices - only show where we have predictions
    test_start_idx = train_len + val_len + (test_len - pred_len) if pred_len < test_len else train_len + val_len
    test_idx = np.arange(test_start_idx, test_start_idx + pred_len)
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot historical data
    ax.plot(train_idx, train_values, label='Train', color='blue', alpha=0.7)
    ax.plot(val_idx, val_values, label='Validation', color='green', alpha=0.7)
    # Plot all test values
    test_idx_all = np.arange(train_len + val_len, train_len + val_len + test_len)
    ax.plot(test_idx_all, test_values, label='Test (Actual)', color='orange', alpha=0.7, linewidth=2)
    # Plot only the part where we have predictions
    ax.plot(test_idx, test_values_for_pred, label='Test (Predicted Range)', color='orange', alpha=0.9, linewidth=2.5)
    
    # Plot predictions
    ax.plot(test_idx, test_pred_inv, label='LSTM Forecast', 
            color='red', linestyle='--', linewidth=2, marker='o', markersize=4)
    
    # Plot baselines (ensure they match prediction length)
    for name, pred_inv in baseline_preds_inv.items():
        if len(pred_inv) != pred_len:
            # Trim or pad to match prediction length
            if len(pred_inv) > pred_len:
                pred_inv = pred_inv[-pred_len:]
            else:
                # Pad with last value
                last_val = pred_inv[-1] if len(pred_inv) > 0 else 0
                pred_inv = np.concatenate([np.full(pred_len - len(pred_inv), last_val), pred_inv])
        ax.plot(test_idx, pred_inv, label=f'{name} Baseline', 
                linestyle='--', alpha=0.6, linewidth=1.5)
    
    ax.set_xlabel('Week Index')
    ax.set_ylabel('Postings Count')
    ax.set_title(title)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Add vertical lines to separate splits
    ax.axvline(x=train_len, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    ax.axvline(x=train_len + val_len, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    ax.text(train_len / 2, ax.get_ylim()[1] * 0.95, 'Train', 
            ha='center', fontsize=8, alpha=0.7)
    ax.text(train_len + val_len / 2, ax.get_ylim()[1] * 0.95, 'Val', 
            ha='center', fontsize=8, alpha=0.7)
    ax.text(train_len + val_len + test_len / 2, ax.get_ylim()[1] * 0.95, 'Test', 
            ha='center', fontsize=8, alpha=0.7)
    
    plt.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved forecast plot to {save_path}")


def save_metrics(metrics: Dict, save_path: Path):
    """Save metrics to JSON file."""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {save_path}")
