"""
Time series dataset utilities for creating sliding windows.
Prevents data leakage by ensuring proper train/val/test splits.
"""
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Tuple, Optional
import pickle
from pathlib import Path


class TimeSeriesDataset(Dataset):
    """
    Dataset for time series forecasting with sliding windows.
    Creates sequences of length `window_size` to predict the next value.
    """
    
    def __init__(self, data: np.ndarray, window_size: int):
        """
        Initialize time series dataset.
        
        Args:
            data: 1D array of time series values
            window_size: Length of input sequence
        """
        self.data = data
        self.window_size = window_size
        
        # Create sequences
        self.X = []
        self.y = []
        
        for i in range(len(data) - window_size):
            self.X.append(data[i:i + window_size])
            self.y.append(data[i + window_size])
        
        self.X = np.array(self.X, dtype=np.float32)
        self.y = np.array(self.y, dtype=np.float32)
        
        # Reshape for LSTM: (samples, sequence_length, features)
        self.X = self.X.reshape((len(self.X), window_size, 1))
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, np.ndarray]:
        return self.X[idx], self.y[idx]


def split_time_series(
    data: pd.DataFrame,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    date_col: str = 'week_start',
    value_col: str = 'postings_count'
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split time series data chronologically (NO SHUFFLE).
    
    Args:
        data: DataFrame with date and value columns
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing (must sum to 1.0)
        date_col: Name of date column
        value_col: Name of value column
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Split ratios must sum to 1.0"
    
    # Ensure data is sorted by date
    data = data.sort_values(date_col).reset_index(drop=True)
    
    n = len(data)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_df = data.iloc[:train_end].copy()
    val_df = data.iloc[train_end:val_end].copy()
    test_df = data.iloc[val_end:].copy()
    
    return train_df, val_df, test_df


def prepare_datasets(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    window_size: int,
    value_col: str = 'postings_count',
    scaler_type: str = 'standard',
    scaler: Optional[object] = None
) -> Tuple[TimeSeriesDataset, TimeSeriesDataset, TimeSeriesDataset, object]:
    """
    Prepare datasets with proper scaling to prevent data leakage.
    
    IMPORTANT: Scaler is fitted ONLY on training data, then applied to val/test.
    
    Args:
        train_df: Training DataFrame
        val_df: Validation DataFrame
        test_df: Test DataFrame
        window_size: Sequence length
        value_col: Column name for values
        scaler_type: 'standard' or 'minmax'
        scaler: Optional pre-fitted scaler (for inference)
        
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset, scaler)
    """
    # Extract values
    train_values = train_df[value_col].values.reshape(-1, 1)
    val_values = val_df[value_col].values.reshape(-1, 1)
    test_values = test_df[value_col].values.reshape(-1, 1)
    
    # Fit scaler on TRAIN ONLY
    if scaler is None:
        if scaler_type == 'standard':
            scaler = StandardScaler()
        elif scaler_type == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaler_type: {scaler_type}")
        
        scaler.fit(train_values)
    
    # Transform all splits using the same scaler
    train_scaled = scaler.transform(train_values).flatten()
    val_scaled = scaler.transform(val_values).flatten()
    test_scaled = scaler.transform(test_values).flatten()
    
    # Create datasets
    train_dataset = TimeSeriesDataset(train_scaled, window_size)
    val_dataset = TimeSeriesDataset(val_scaled, window_size)
    test_dataset = TimeSeriesDataset(test_scaled, window_size)
    
    return train_dataset, val_dataset, test_dataset, scaler


def save_scaler(scaler: object, path: Path):
    """Save scaler to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(scaler, f)


def load_scaler(path: Path) -> object:
    """Load scaler from disk."""
    with open(path, 'rb') as f:
        return pickle.load(f)


def create_dataloaders(
    train_dataset: TimeSeriesDataset,
    val_dataset: TimeSeriesDataset,
    test_dataset: TimeSeriesDataset,
    batch_size: int = 32
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Create PyTorch DataLoaders."""
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False
    )
    
    return train_loader, val_loader, test_loader
