# Better to use datetime types YYYY-MM-DDTHH:MM:SS for timestamps. For now, it will be a string.

import json
import requests
from typing import List, Optional, Dict, Any, Literal, Union
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
from .utils import (
    forecast_to_nolano_format,
    nolano_forecast_to_dataframe,
    validate_nolano_series_format
)

# Optional matplotlib import for plotting
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


@dataclass
class NolanoForecast:
    """A class for Nolano time series forecasting results."""
    forecast_timestamps: List[str]
    lower_bound: List[float]
    median: List[float]
    upper_bound: List[float]
    historical_timestamps: Optional[List[str]] = None
    historical_values: Optional[List[float]] = None
    
    def __post_init__(self):
        """Validate input data."""
        self._validate_inputs()
    
    def _validate_inputs(self) -> None:
        """Validate input data dimensions."""
        lengths = [
            len(self.forecast_timestamps),
            len(self.lower_bound),
            len(self.median),
            len(self.upper_bound)
        ]
        
        if not all(length == lengths[0] for length in lengths):
            raise ValueError("All forecast arrays must have the same length")
        
        # Validate historical data if present
        if self.historical_timestamps is not None and self.historical_values is not None:
            if len(self.historical_timestamps) != len(self.historical_values):
                raise ValueError("Historical timestamps and values must have the same length")
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert forecast to pandas DataFrame."""
        return nolano_forecast_to_dataframe(
            self.forecast_timestamps,
            self.lower_bound,
            self.median,
            self.upper_bound
        )
    
    def plot(self, height: int = 4, width: int = 8, save_path: Optional[str] = None) -> None:
        """Display actual data, predicted forecasts, and confidence interval.
        
        Args:
            height: Plot height in inches. Defaults to 4.
            width: Plot width in inches. Defaults to 8.
            save_path: Path to save the plot as file. If None, displays the plot. Defaults to None.
            
        Raises:
            ImportError: If matplotlib is not installed
            ValueError: If historical data is not available
        """
        if not HAS_MATPLOTLIB:
            raise ImportError(
                "matplotlib is required for plotting. Install it with: pip install matplotlib"
            )
        
        if self.historical_values is None or self.historical_timestamps is None:
            raise ValueError(
                "Historical data is not available. "
                "Make sure to use forecast methods that capture historical context."
            )
        
        context_size = len(self.historical_values)
        horizon_length = len(self.median)
        forecast_indices = range(context_size, context_size + horizon_length)
        historical_indices = range(context_size)

        plt.figure(figsize=(width, height))
        
        # Plot historical data
        plt.plot(
            historical_indices,
            self.historical_values, 
            color="royalblue", 
            label="Historical data"
        )
        
        # Plot median forecast
        plt.plot(
            forecast_indices, 
            self.median, 
            color="green", 
            label="Median forecast"
        )
        
        # Plot confidence interval
        plt.fill_between(
            forecast_indices,
            self.lower_bound,
            self.upper_bound,
            color="tomato",
            alpha=0.3,
            label="Prediction interval"
        )
        
        plt.legend()
        plt.grid(True)
        plt.xlabel("Time Period")
        plt.ylabel("Value")
        plt.title("Time Series Forecast")
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()  # Close the figure to free memory
        else:
            plt.show()
    
    def evaluate(self, actual_values: List[float], prediction_type: str = 'median') -> Dict[str, float]:
        """Calculate evaluation metrics comparing forecast to actual values.
        
        Args:
            actual_values (List[float]): Actual observed values for the forecast period
            prediction_type (str): Which forecast values to use ('median', 'lower_bound', 'upper_bound'). 
                                 Defaults to 'median'.
                                 
        Returns:
            Dict[str, float]: Dictionary containing evaluation metrics:
                - mae: Mean Absolute Error
                - wape: Weighted Absolute Percentage Error (as percentage)
                
        Raises:
            ValueError: If actual_values length doesn't match forecast length or invalid prediction_type
            ImportError: If required utility functions are not available
            
        Example:
            >>> # After generating a forecast
            >>> actual_values = [105, 110, 108, 115, 120]  # Actual values for forecast period
            >>> metrics = forecast.evaluate(actual_values)
            >>> print(f"MAE: {metrics['mae']:.2f}")
            >>> print(f"WAPE: {metrics['wape']:.2f}%")
        """
        from .utils import calculate_forecast_metrics
        
        # Validate inputs
        if len(actual_values) != len(self.median):
            raise ValueError(
                f"Length mismatch: actual_values ({len(actual_values)}) != "
                f"forecast length ({len(self.median)})"
            )
        
        # Select prediction values based on type
        if prediction_type == 'median':
            predicted_values = self.median
        elif prediction_type == 'lower_bound':
            predicted_values = self.lower_bound
        elif prediction_type == 'upper_bound':
            predicted_values = self.upper_bound
        else:
            raise ValueError(
                f"Invalid prediction_type '{prediction_type}'. "
                "Must be one of: 'median', 'lower_bound', 'upper_bound'"
            )
        
        # Calculate metrics
        return calculate_forecast_metrics(actual_values, predicted_values)
    
    def mae(self, actual_values: List[float], prediction_type: str = 'median') -> float:
        """Calculate Mean Absolute Error (MAE) for the forecast.
        
        Convenience method for calculating MAE directly.
        
        Args:
            actual_values (List[float]): Actual observed values for the forecast period
            prediction_type (str): Which forecast values to use. Defaults to 'median'.
            
        Returns:
            float: Mean Absolute Error
            
        Example:
            >>> mae_score = forecast.mae(actual_values)
            >>> print(f"MAE: {mae_score:.2f}")
        """
        metrics = self.evaluate(actual_values, prediction_type)
        return metrics['mae']
    
    def wape(self, actual_values: List[float], prediction_type: str = 'median') -> float:
        """Calculate Weighted Absolute Percentage Error (WAPE) for the forecast.
        
        Convenience method for calculating WAPE directly.
        
        Args:
            actual_values (List[float]): Actual observed values for the forecast period
            prediction_type (str): Which forecast values to use. Defaults to 'median'.
            
        Returns:
            float: Weighted Absolute Percentage Error as a percentage
            
        Example:
            >>> wape_score = forecast.wape(actual_values)
            >>> print(f"WAPE: {wape_score:.2f}%")
        """
        metrics = self.evaluate(actual_values, prediction_type)
        return metrics['wape']


class NolanoClient:
    """Client for interacting with Nolano's time series forecasting API."""    
    # Available Nolano models
    AVAILABLE_MODELS = [
        "forecast-model-1",  # Primary Forecasting Model
        "forecast-model-2",  # Alternative Forecasting Model  
        "forecast-model-3",  # Advanced Forecasting Model
        "forecast-model-4"   # Next-Generation Model
    ]
    
    VALID_FREQUENCIES = [
        "Seconds", "Minutes", "Hours", "Daily", 
        "Weekly", "Monthly", "Quarterly", "Yearly"
    ]
    
    def __init__(self, api_url: str, api_key: str, model_id: Optional[str] = None):
        """Initialize Nolano client with API credentials.
        
        Args:
            api_key (str): API key for authentication
            model_id (str, optional): Default model ID to use. Defaults to 'forecast-model-1'
        
        Raises:
            ValueError: If model_id is not in available models
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model_id = model_id or "forecast-model-1"
        
        if self.model_id not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model ID must be one of: {self.AVAILABLE_MODELS}")
    
    def _get_headers(self, model_id: Optional[str] = None) -> Dict[str, str]:
        """Get request headers for API calls.
        
        Args:
            model_id (str, optional): Override default model ID
            
        Returns:
            Dict[str, str]: Headers for API request
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        if model_id or self.model_id:
            headers['X-Model-Id'] = model_id or self.model_id
            
        return headers
    
    def verify_api_key(self) -> Dict[str, Any]:
        """Verify the API key with Nolano API.
        
        Returns:
            Dict[str, Any]: Verification result with status and details
            
        Raises:
            requests.exceptions.HTTPError: If API request fails
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        url = f"{self.api_url}/verify"
        
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # If we get here, the API key is valid
            result = {
                'valid': True,
                'message': 'API key is valid'
            }
            
            # Try to parse JSON response if available
            try:
                api_response = response.json()
                result.update(api_response)
            except json.JSONDecodeError:
                # If no JSON response, just return our basic result
                pass
                
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {
                    'valid': False,
                    'status': 'unauthorized',
                    'message': 'Invalid API key'
                }
            elif e.response.status_code == 403:
                return {
                    'valid': False,
                    'status': 'forbidden',
                    'message': 'API key does not have required permissions'
                }
            else:
                raise requests.exceptions.HTTPError(
                    f"API key verification failed: {str(e)}"
                ) from e
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.HTTPError(
                f"Network error during API key verification: {str(e)}"
            ) from e
    
    def forecast(
        self,
        series: List[Dict[str, Any]],
        forecast_horizon: int,
        data_frequency: str,
        forecast_frequency: str,
        confidence: float = 0.95,
        model_id: Optional[str] = None
    ) -> NolanoForecast:
        """Generate a time series forecast using Nolano API.
        
        Args:
            series (List[Dict]): List containing time series data. Each dict should have
                'timestamps' (List[str]) and 'values' (List[float]) keys
            forecast_horizon (int): Number of future periods to predict
            data_frequency (str): Frequency of input data (e.g., "Daily", "Hourly")
            forecast_frequency (str): Desired forecast frequency (must match data_frequency)
            confidence (float): Confidence level between 0 and 1. Defaults to 0.95
            model_id (str, optional): Override default model ID
            
        Returns:
            NolanoForecast: Forecast results with timestamps and prediction intervals
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.HTTPError: If API request fails
        """
        # Validate inputs
        if not series:
            raise ValueError("At least one time series is required")
        
        if len(series) > 1:
            raise ValueError("Nolano API currently supports only one time series")
        
        if data_frequency not in self.VALID_FREQUENCIES:
            raise ValueError(f"data_frequency must be one of: {self.VALID_FREQUENCIES}")
        
        if forecast_frequency not in self.VALID_FREQUENCIES:
            raise ValueError(f"forecast_frequency must be one of: {self.VALID_FREQUENCIES}")
        
        if data_frequency != forecast_frequency:
            raise ValueError("forecast_frequency must match data_frequency")
        
        if not 0 < confidence < 1:
            raise ValueError("confidence must be between 0 and 1")
        
        if forecast_horizon <= 0:
            raise ValueError("forecast_horizon must be positive")
        
        # Validate series structure
        validate_nolano_series_format(series)
        
        # Prepare request payload
        payload = {
            "series": series,
            "forecast_horizon": forecast_horizon,
            "data_frequency": data_frequency,
            "forecast_frequency": forecast_frequency,
            "confidence": confidence
        }
        
        # Make API request
        headers = self._get_headers(model_id)
        url = f"{self.api_url}/forecast"
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.HTTPError(
                f"Nolano API request failed: {str(e)}"
            ) from e
        
        # Parse response
        try:
            result = response.json()
            
            # Extract historical data from the input series
            historical_timestamps = None
            historical_values = None
            if series and len(series) > 0:
                historical_timestamps = series[0].get('timestamps', [])
                historical_values = series[0].get('values', [])
            
            return NolanoForecast(
                forecast_timestamps=result['forecast_timestamps'],
                lower_bound=result['lower_bound'],
                median=result['median'],
                upper_bound=result['upper_bound'],
                historical_timestamps=historical_timestamps,
                historical_values=historical_values
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid response format from Nolano API: {str(e)}") from e
    
    def forecast_from_dataframe(
        self,
        df: pd.DataFrame,
        timestamp_col: str,
        value_col: str,
        forecast_horizon: int,
        data_frequency: str,
        forecast_frequency: Optional[str] = None,
        confidence: float = 0.95,
        model_id: Optional[str] = None
    ) -> NolanoForecast:
        """Generate forecast from pandas DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame with time series data
            timestamp_col (str): Column name containing timestamps
            value_col (str): Column name containing values to forecast
            forecast_horizon (int): Number of future periods to predict
            data_frequency (str): Frequency of input data
            forecast_frequency (str, optional): Desired forecast frequency. 
                Defaults to data_frequency
            confidence (float): Confidence level. Defaults to 0.95
            model_id (str, optional): Override default model ID
            
        Returns:
            NolanoForecast: Forecast results
            
        Raises:
            KeyError: If specified columns not found in DataFrame
        """
        if timestamp_col not in df.columns:
            raise KeyError(f"Timestamp column '{timestamp_col}' not found in DataFrame")
        
        if value_col not in df.columns:
            raise KeyError(f"Value column '{value_col}' not found in DataFrame")
        
        # Convert DataFrame to Nolano format
        series_data = forecast_to_nolano_format(df, timestamp_col, value_col)
        series = [series_data]
        
        return self.forecast(
            series=series,
            forecast_horizon=forecast_horizon,
            data_frequency=data_frequency,
            forecast_frequency=forecast_frequency or data_frequency,
            confidence=confidence,
            model_id=model_id
        ) 