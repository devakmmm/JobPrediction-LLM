"""
Tests for time series dataset utilities.
"""
import pytest
import pandas as pd
import numpy as np
from ml.datasets import split_time_series, TimeSeriesDataset, prepare_datasets


def test_time_series_dataset():
    """Test TimeSeriesDataset creates correct windows."""
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float32)
    window_size = 3
    
    dataset = TimeSeriesDataset(data, window_size)
    
    assert len(dataset) == len(data) - window_size  # 10 - 3 = 7
    
    # Check first sample
    X, y = dataset[0]
    assert X.shape == (window_size, 1)
    assert np.array_equal(X.flatten(), [1, 2, 3])
    assert y == 4
    
    # Check last sample
    X, y = dataset[-1]
    assert np.array_equal(X.flatten(), [7, 8, 9])
    assert y == 10


def test_split_time_series():
    """Test chronological split (no shuffle)."""
    dates = pd.date_range('2022-01-01', periods=100, freq='W')
    df = pd.DataFrame({
        'week_start': dates,
        'postings_count': np.arange(100)
    })
    
    train_df, val_df, test_df = split_time_series(
        df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
    )
    
    assert len(train_df) == 70
    assert len(val_df) == 15
    assert len(test_df) == 15
    
    # Check chronological order
    assert train_df['week_start'].min() < val_df['week_start'].min()
    assert val_df['week_start'].min() < test_df['week_start'].min()
    assert train_df['week_start'].max() < val_df['week_start'].min()
    assert val_df['week_start'].max() < test_df['week_start'].min()


def test_prepare_datasets_no_leakage():
    """Test that scaler is fitted only on training data."""
    # Create synthetic data with different scales
    train_values = np.array([10, 20, 30, 40, 50])
    val_values = np.array([100, 200, 300])  # Much larger scale
    test_values = np.array([1000, 2000, 3000])  # Even larger
    
    train_df = pd.DataFrame({
        'week_start': pd.date_range('2022-01-01', periods=5, freq='W'),
        'postings_count': train_values
    })
    val_df = pd.DataFrame({
        'week_start': pd.date_range('2022-02-05', periods=3, freq='W'),
        'postings_count': val_values
    })
    test_df = pd.DataFrame({
        'week_start': pd.date_range('2022-02-26', periods=3, freq='W'),
        'postings_count': test_values
    })
    
    train_ds, val_ds, test_ds, scaler = prepare_datasets(
        train_df, val_df, test_df, window_size=2
    )
    
    # Scaler should be fitted on train only
    # After scaling, train mean should be ~0
    train_data = train_ds.data
    assert np.abs(np.mean(train_data)) < 0.1  # Mean should be ~0 after standardization
    
    # Val and test should be scaled using train's parameters
    # So they might not have mean 0, but that's expected (no leakage)
    assert len(train_ds) > 0
    assert len(val_ds) > 0
    assert len(test_ds) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
