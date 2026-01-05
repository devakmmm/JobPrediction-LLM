"""
PyTorch LSTM model for time series forecasting.
"""
import torch
import torch.nn as nn
from typing import Tuple


class LSTMForecaster(nn.Module):
    """
    LSTM model for univariate time series forecasting.
    
    Architecture:
    - LSTM layer(s) with hidden units
    - Fully connected output layer for single-step prediction
    """
    
    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2
    ):
        """
        Initialize LSTM forecaster.
        
        Args:
            input_size: Number of input features (1 for univariate)
            hidden_size: Number of LSTM hidden units
            num_layers: Number of LSTM layers
            dropout: Dropout rate between LSTM layers
        """
        super(LSTMForecaster, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Output layer (maps hidden state to scalar prediction)
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)
            
        Returns:
            Prediction tensor of shape (batch_size, 1)
        """
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Take the last output from the sequence
        last_output = lstm_out[:, -1, :]  # (batch_size, hidden_size)
        
        # Map to prediction
        prediction = self.fc(last_output)  # (batch_size, 1)
        
        return prediction
    
    def predict_step(self, x: torch.Tensor) -> torch.Tensor:
        """Prediction step (same as forward, but sets model to eval mode)."""
        self.eval()
        with torch.no_grad():
            return self.forward(x)


def create_model(
    input_size: int = 1,
    hidden_size: int = 64,
    num_layers: int = 2,
    dropout: float = 0.2
) -> LSTMForecaster:
    """
    Factory function to create LSTM model.
    
    Returns:
        Initialized LSTMForecaster model
    """
    return LSTMForecaster(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers,
        dropout=dropout
    )
