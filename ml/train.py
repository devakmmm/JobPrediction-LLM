"""
End-to-end training script for LSTM job market demand forecaster.
"""
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
import json

from ml.models import create_model
from ml.datasets import (
    split_time_series, prepare_datasets, create_dataloaders,
    save_scaler
)
from ml.baselines import (
    NaiveBaseline, MovingAverageBaseline, ARIMABaseline,
    compute_baseline_metrics
)
from ml.evaluate import compute_metrics, plot_forecasts, save_metrics
from ml.export import export_model


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    n_batches = 0
    
    for X_batch, y_batch in dataloader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)
        
        optimizer.zero_grad()
        predictions = model(X_batch).squeeze()
        loss = criterion(predictions, y_batch)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        n_batches += 1
    
    return total_loss / n_batches if n_batches > 0 else 0.0


def validate(model, dataloader, criterion, device):
    """Validate model."""
    model.eval()
    total_loss = 0.0
    n_batches = 0
    
    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            predictions = model(X_batch).squeeze()
            loss = criterion(predictions, y_batch)
            
            total_loss += loss.item()
            n_batches += 1
    
    return total_loss / n_batches if n_batches > 0 else 0.0


def predict_sequence(model, initial_sequence: np.ndarray, horizon: int, device) -> np.ndarray:
    """
    Make recursive predictions for multiple steps ahead.
    
    Args:
        model: Trained model
        initial_sequence: Initial window of data (window_size, 1)
        horizon: Number of steps to predict ahead
        device: Device to run on
        
    Returns:
        Array of predictions (horizon,)
    """
    model.eval()
    predictions = []
    
    # Start with initial sequence
    current_sequence = initial_sequence.copy()
    
    with torch.no_grad():
        for _ in range(horizon):
            # Prepare input (1, window_size, 1)
            X = torch.FloatTensor(current_sequence).unsqueeze(0).to(device)
            
            # Predict next value
            pred = model(X).cpu().numpy()[0, 0]
            predictions.append(pred)
            
            # Update sequence: remove first, add prediction at end
            current_sequence = np.concatenate([
                current_sequence[1:],
                np.array([[pred]], dtype=np.float32)
            ])
    
    return np.array(predictions)


def main():
    parser = argparse.ArgumentParser(description="Train LSTM job market demand forecaster")
    parser.add_argument("--csv", required=True, help="Path to processed CSV file")
    parser.add_argument("--role", required=True, help="Job role name")
    parser.add_argument("--location", required=True, help="Location name")
    parser.add_argument("--window", type=int, default=12, help="Window size (default: 12)")
    parser.add_argument("--hidden-size", type=int, default=64, help="LSTM hidden size (default: 64)")
    parser.add_argument("--num-layers", type=int, default=2, help="Number of LSTM layers (default: 2)")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs (default: 50)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (default: 32)")
    parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate (default: 0.001)")
    parser.add_argument("--output-dir", default="backend/app/artifacts", help="Output directory for artifacts")
    parser.add_argument("--reports-dir", default="reports", help="Reports directory")
    parser.add_argument("--device", default="auto", help="Device: auto, cpu, or cuda")
    
    args = parser.parse_args()
    
    # Device setup
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    
    print(f"Using device: {device}")
    
    # Load data
    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    df['week_start'] = pd.to_datetime(df['week_start']).dt.date
    
    # Ensure we have enough data
    if len(df) < args.window + 10:
        raise ValueError(
            f"Insufficient data: need at least {args.window + 10} weeks, "
            f"got {len(df)}"
        )
    
    # Split data chronologically
    print("Splitting data into train/val/test...")
    train_df, val_df, test_df = split_time_series(
        df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
    )
    
    print(f"  Train: {len(train_df)} weeks ({train_df['week_start'].min()} to {train_df['week_start'].max()})")
    print(f"  Val: {len(val_df)} weeks ({val_df['week_start'].min()} to {val_df['week_start'].max()})")
    print(f"  Test: {len(test_df)} weeks ({test_df['week_start'].min()} to {test_df['week_start'].max()})")
    
    # Prepare datasets with scaling
    print("Preparing datasets with scaling...")
    train_ds, val_ds, test_ds, scaler = prepare_datasets(
        train_df, val_df, test_df,
        window_size=args.window,
        value_col='postings_count',
        scaler_type='standard'
    )
    
    print(f"  Train sequences: {len(train_ds)}")
    print(f"  Val sequences: {len(val_ds)}")
    print(f"  Test sequences: {len(test_ds)}")
    
    # Create data loaders
    train_loader, val_loader, test_loader = create_dataloaders(
        train_ds, val_ds, test_ds, batch_size=args.batch_size
    )
    
    # Create model
    print("Creating LSTM model...")
    model = create_model(
        input_size=1,
        hidden_size=args.hidden_size,
        num_layers=args.num_layers,
        dropout=0.2
    ).to(device)
    
    print(f"  Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Training setup
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    
    # Training loop
    print(f"\nTraining for {args.epochs} epochs...")
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0
    
    train_losses = []
    val_losses = []
    
    for epoch in range(args.epochs):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = validate(model, val_loader, criterion, device)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1}/{args.epochs} - Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping at epoch {epoch+1}")
                break
    
    print(f"\nTraining completed. Best validation loss: {best_val_loss:.6f}")
    
    # Evaluation on test set
    print("\nEvaluating on test set...")
    
    # Get test predictions (1-step ahead)
    model.eval()
    test_predictions = []
    test_targets = []
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            preds = model(X_batch).squeeze().cpu().numpy()
            test_predictions.extend(preds)
            test_targets.extend(y_batch.numpy())
    
    test_predictions = np.array(test_predictions)
    test_targets = np.array(test_targets)
    
    # Compute LSTM metrics
    lstm_metrics = compute_metrics(test_targets, test_predictions)
    print(f"  LSTM RMSE: {lstm_metrics['rmse']:.4f}")
    print(f"  LSTM MAPE: {lstm_metrics['mape']:.2f}%")
    print(f"  LSTM Directional Accuracy: {lstm_metrics['directional_accuracy']:.2f}%")
    
    # Baseline predictions
    print("\nEvaluating baselines...")
    
    # Get raw test values for baselines
    test_values_raw = test_df['postings_count'].values
    train_values_raw = train_df['postings_count'].values
    val_values_raw = val_df['postings_count'].values
    
    # Fit baselines on training data
    naive = NaiveBaseline()
    naive.fit(train_values_raw)
    
    ma = MovingAverageBaseline(window=4)
    ma.fit(train_values_raw)
    
    baseline_predictions = {}
    baseline_metrics = {}
    
    # Naive baseline
    naive_pred_raw = naive.predict(len(test_values_raw))
    naive_metrics = compute_baseline_metrics(test_values_raw, naive_pred_raw)
    baseline_predictions["Naive"] = naive_pred_raw
    baseline_metrics["naive"] = naive_metrics
    print(f"  Naive RMSE: {naive_metrics['rmse']:.4f}")
    
    # Moving average baseline
    ma_pred_raw = ma.predict(len(test_values_raw))
    ma_metrics = compute_baseline_metrics(test_values_raw, ma_pred_raw)
    baseline_predictions["MovingAvg"] = ma_pred_raw
    baseline_metrics["moving_average"] = ma_metrics
    print(f"  Moving Avg RMSE: {ma_metrics['rmse']:.4f}")
    
    # ARIMA baseline (optional)
    try:
        arima = ARIMABaseline(order=(1, 1, 1))
        arima.fit(train_values_raw)
        arima_pred_raw = arima.predict(len(test_values_raw))
        arima_metrics = compute_baseline_metrics(test_values_raw, arima_pred_raw)
        baseline_predictions["ARIMA"] = arima_pred_raw
        baseline_metrics["arima"] = arima_metrics
        print(f"  ARIMA RMSE: {arima_metrics['rmse']:.4f}")
    except Exception as e:
        print(f"  ARIMA baseline skipped: {e}")
    
    # Prepare predictions for plotting (need to transform to scaled space for baselines)
    # Actually, let's plot in raw space for clarity
    test_pred_raw = scaler.inverse_transform(test_predictions.reshape(-1, 1)).flatten()
    test_targets_raw = test_values_raw
    
    # Create plot
    print("\nGenerating forecast plot...")
    plot_path = Path(args.reports_dir) / "forecast_plot.png"
    
    # For plotting, we need to transform baseline predictions back to scaled
    # But actually, let's just plot everything in raw space
    baseline_preds_scaled = {}
    for name, pred_raw in baseline_predictions.items():
        baseline_preds_scaled[name] = scaler.transform(pred_raw.reshape(-1, 1)).flatten()
    
    plot_forecasts(
        train_values_raw,
        val_values_raw,
        test_targets_raw,
        test_predictions,  # Already scaled
        baseline_preds_scaled,
        scaler,
        plot_path,
        title=f"Job Market Forecast: {args.role} ({args.location})"
    )
    
    # Save metrics
    all_metrics = {
        "lstm": lstm_metrics,
        "baselines": baseline_metrics,
        "model_config": {
            "window_size": args.window,
            "hidden_size": args.hidden_size,
            "num_layers": args.num_layers,
            "epochs_trained": len(train_losses),
        }
    }
    
    metrics_path = Path(args.reports_dir) / "metrics.json"
    save_metrics(all_metrics, metrics_path)
    
    # Export model artifacts
    print("\nExporting model artifacts...")
    role_slug = args.role.lower().replace(" ", "_")
    location_slug = args.location.lower().replace(" ", "_").replace(",", "")
    artifacts_dir = Path(args.output_dir) / f"{role_slug}_{location_slug}"
    
    export_model(
        model=model,
        scaler=scaler,
        window_size=args.window,
        metrics=all_metrics,
        role=args.role,
        location=args.location,
        output_dir=artifacts_dir,
        train_date_range=(train_df['week_start'].min(), train_df['week_start'].max())
    )
    
    print("\nTraining and evaluation complete!")
    print(f"  Artifacts saved to: {artifacts_dir}")
    print(f"  Metrics saved to: {metrics_path}")
    print(f"  Plot saved to: {plot_path}")


if __name__ == "__main__":
    main()
