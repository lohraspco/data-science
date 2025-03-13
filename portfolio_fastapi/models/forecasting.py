import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
import json

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        # Initialize cell state
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        return out

class TimeSeriesForecaster:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.sequence_length = 10
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def prepare_data(self, data: str) -> tuple:
        """
        Prepare the data for training/prediction.
        
        Args:
            data (str): JSON string containing time series data
            
        Returns:
            tuple: (X, y) tensors for training
        """
        try:
            # Parse JSON data
            df = pd.DataFrame(json.loads(data))
            
            # Ensure data is sorted by date
            df = df.sort_values('date')
            
            # Scale the data
            scaled_data = self.scaler.fit_transform(df[['value']].values)
            
            # Create sequences
            X, y = [], []
            for i in range(len(scaled_data) - self.sequence_length):
                X.append(scaled_data[i:(i + self.sequence_length)])
                y.append(scaled_data[i + self.sequence_length])
            
            # Convert to PyTorch tensors
            X = torch.FloatTensor(np.array(X)).to(self.device)
            y = torch.FloatTensor(np.array(y)).to(self.device)
            
            return X, y
        except Exception as e:
            raise ValueError(f"Error preparing data: {str(e)}")

    def build_model(self):
        """Build the LSTM model architecture."""
        self.model = LSTMModel().to(self.device)
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    async def train(self, data: str, epochs: int = 50, batch_size: int = 32):
        """
        Train the model on the provided data.
        
        Args:
            data (str): JSON string containing time series data
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
        """
        try:
            X, y = self.prepare_data(data)
            
            if self.model is None:
                self.build_model()
            
            self.model.train()
            for epoch in range(epochs):
                # Forward pass
                outputs = self.model(X)
                loss = self.criterion(outputs, y)
                
                # Backward pass and optimize
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                if (epoch + 1) % 10 == 0:
                    print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
                    
        except Exception as e:
            raise ValueError(f"Error training model: {str(e)}")

    async def predict(self, data: str) -> dict:
        """
        Make predictions on the provided data.
        
        Args:
            data (str): JSON string containing time series data
            
        Returns:
            dict: Dictionary containing predictions and actual values
        """
        try:
            X, y = self.prepare_data(data)
            
            if self.model is None:
                raise ValueError("Model not trained yet")
            
            self.model.eval()
            with torch.no_grad():
                predictions = self.model(X)
            
            # Convert to numpy arrays and inverse transform
            predictions = predictions.cpu().numpy()
            y = y.cpu().numpy()
            
            predictions = self.scaler.inverse_transform(predictions)
            actual_values = self.scaler.inverse_transform(y)
            
            return {
                "predictions": predictions.tolist(),
                "actual_values": actual_values.tolist()
            }
        except Exception as e:
            raise ValueError(f"Error making predictions: {str(e)}") 