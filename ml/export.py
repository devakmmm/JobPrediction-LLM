"""
Export trained model artifacts for inference.
"""
import json
import torch
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from ml.models import LSTMForecaster
from ml.datasets import load_scaler


def export_model(
    model: LSTMForecaster,
    scaler: object,
    window_size: int,
    metrics: Dict[str, Any],
    role: str,
    location: str,
    output_dir: Path,
    train_date_range: tuple = None
):
    """
    Export model artifacts for deployment.
    
    Args:
        model: Trained LSTM model
        scaler: Fitted scaler
        window_size: Window size used for training
        metrics: Training metrics dictionary
        role: Job role name
        location: Location name
        output_dir: Directory to save artifacts
        train_date_range: Tuple of (start_date, end_date) for training data
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = output_dir / "model.pt"
    torch.save({
        'model_state_dict': model.state_dict(),
        'input_size': model.input_size,
        'hidden_size': model.hidden_size,
        'num_layers': model.num_layers,
    }, model_path)
    print(f"Saved model to {model_path}")
    
    # Save scaler
    scaler_path = output_dir / "scaler.pkl"
    import pickle
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Saved scaler to {scaler_path}")
    
    # Save metadata
    metadata = {
        "role": role,
        "location": location,
        "window_size": window_size,
        "model_type": "lstm",
        "model_config": {
            "input_size": model.input_size,
            "hidden_size": model.hidden_size,
            "num_layers": model.num_layers,
        },
        "trained_at": datetime.now().isoformat(),
        "train_date_range": {
            "start": str(train_date_range[0]) if train_date_range else None,
            "end": str(train_date_range[1]) if train_date_range else None,
        },
        "metrics": metrics
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {metadata_path}")


def load_model_artifacts(artifacts_dir: Path) -> tuple:
    """
    Load model artifacts for inference.
    
    Args:
        artifacts_dir: Directory containing model.pt, scaler.pkl, metadata.json
        
    Returns:
        Tuple of (model, scaler, metadata)
    """
    artifacts_dir = Path(artifacts_dir)
    
    # Load metadata
    metadata_path = artifacts_dir / "metadata.json"
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Load model
    model_path = artifacts_dir / "model.pt"
    checkpoint = torch.load(model_path, map_location='cpu')
    
    model = LSTMForecaster(
        input_size=checkpoint['input_size'],
        hidden_size=checkpoint['hidden_size'],
        num_layers=checkpoint['num_layers']
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # Load scaler
    scaler_path = artifacts_dir / "scaler.pkl"
    scaler = load_scaler(scaler_path)
    
    return model, scaler, metadata
