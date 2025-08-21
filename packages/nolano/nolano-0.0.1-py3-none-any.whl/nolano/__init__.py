import logging
import numpy as np
import os
import pandas as pd
from typing import Optional, List, Dict, Any, Union
from .nolano import NolanoClient, NolanoForecast
from .utils import (
    forecast_to_nolano_format,
    nolano_forecast_to_dataframe,
    validate_nolano_series_format,
    convert_confidence_to_quantiles,
    array_split,
    mean_absolute_error,
    weighted_absolute_percentage_error,
    calculate_forecast_metrics
)

__version__ = "0.0.1"

# Export key classes and utilities for external use
__all__ = [
    "Nolano",
    "NolanoClient", 
    "NolanoForecast",
    "forecast_to_nolano_format",
    "nolano_forecast_to_dataframe", 
    "validate_nolano_series_format",
    "convert_confidence_to_quantiles",
    "array_split",
    "mean_absolute_error",
    "weighted_absolute_percentage_error",
    "calculate_forecast_metrics"
]

logger = logging.getLogger("nolano")

_DEFAULT_NOLANO_API_URL = "https://api.nolano.ai"


class Nolano:
    """Client for interacting with Nolano's time series forecasting API.

    This class provides methods to generate forecasts using Nolano's zeroshot
    forecasting models, with support for multiple model types and data frequencies.
    """

    def __init__(self, api_key: Optional[str] = None, model_id: Optional[str] = None):
        """Initialize Nolano client with API credentials.

        Args:
            api_key (str, optional): Nolano API key for authentication. If None, 
                reads from NOLANO_API_KEY environment variable
            model_id (str, optional): Default model ID to use. Defaults to 'forecast-model-1'
        
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        api_url = os.environ.get("NOLANO_API_URL", _DEFAULT_NOLANO_API_URL)
        api_key = api_key or os.environ.get("NOLANO_API_KEY")
        if api_key is None:
            raise ValueError(
                "No API key provided. Set NOLANO_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self._client = NolanoClient(api_url,api_key, model_id)
        logger.info(f"Nolano client initialized with model: {self._client.model_id}")

    @property
    def model_id(self) -> str:
        """Get the current default model ID."""
        return self._client.model_id

    @model_id.setter
    def model_id(self, value: str) -> None:
        """Set the default model ID."""
        if value not in self._client.AVAILABLE_MODELS:
            raise ValueError(f"Model ID must be one of: {self._client.AVAILABLE_MODELS}")
        self._client.model_id = value

    def list_models(self) -> List[str]:
        """List available Nolano forecasting models.

        Returns:
            List[str]: Available Nolano model IDs with descriptions.
        """
        models = []
        model_descriptions = {
            "forecast-model-1": "Primary Forecasting Model - Optimized for general forecasting tasks",
            "forecast-model-2": "Alternative Forecasting Model - Enhanced accuracy for complex patterns", 
            "forecast-model-3": "Advanced Forecasting Model - High-frequency data processing",
            "forecast-model-4": "Next-Generation Model - Deep learning with ensemble methods"
        }
        
        for model_id in self._client.AVAILABLE_MODELS:
            description = model_descriptions.get(model_id, "Specialized forecasting model")
            models.append(f"{model_id}: {description}")
        
        return models

    def forecast(
        self,
        dataset: pd.DataFrame,
        target_col: str,
        timestamp_col: str,
        forecast_horizon: int,
        data_frequency: str,
        forecast_frequency: Optional[str] = None,
        confidence: float = 0.95,
        model_id: Optional[str] = None
    ) -> NolanoForecast:
        """Generate time series forecasts using Nolano API.

        Args:
            dataset (pd.DataFrame): Input time series data.
            target_col (str): Column containing values to forecast.
            timestamp_col (str): Column containing timestamps.
            forecast_horizon (int): Number of future periods to predict.
            data_frequency (str): Frequency of input data ("Daily", "Hourly", etc.).
            forecast_frequency (str, optional): Desired forecast frequency. 
                Defaults to data_frequency.
            confidence (float): Confidence level (0-1). Defaults to 0.95.
            model_id (str, optional): Nolano model ID to use. If None, uses default.

        Returns:
            NolanoForecast: Forecast results with timestamps and prediction intervals.

        Raises:
            ValueError: If parameters are invalid.
            KeyError: If specified columns not found in dataset.
        """
        return self._client.forecast_from_dataframe(
            df=dataset,
            timestamp_col=timestamp_col,
            value_col=target_col,
            forecast_horizon=forecast_horizon,
            data_frequency=data_frequency,
            forecast_frequency=forecast_frequency or data_frequency,
            confidence=confidence,
            model_id=model_id
        )

    def forecast_from_series(
        self,
        series: List[Dict[str, Any]],
        forecast_horizon: int,
        data_frequency: str,
        forecast_frequency: Optional[str] = None,
        confidence: float = 0.95,
        model_id: Optional[str] = None
    ) -> NolanoForecast:
        """Generate forecast from raw series data in Nolano format.

        Args:
            series (List[Dict]): List containing time series data. Each dict should have
                'timestamps' (List[str]) and 'values' (List[float]) keys
            forecast_horizon (int): Number of future periods to predict.
            data_frequency (str): Frequency of input data.
            forecast_frequency (str, optional): Desired forecast frequency.
            confidence (float): Confidence level (0-1). Defaults to 0.95.
            model_id (str, optional): Nolano model ID to use.

        Returns:
            NolanoForecast: Forecast results.
        """
        return self._client.forecast(
            series=series,
            forecast_horizon=forecast_horizon,
            data_frequency=data_frequency,
            forecast_frequency=forecast_frequency or data_frequency,
            confidence=confidence,
            model_id=model_id
        )

    def validate_data(
        self,
        dataset: pd.DataFrame,
        target_col: str,
        timestamp_col: str
    ) -> Dict[str, Any]:
        """Validate dataset for forecasting.

        Args:
            dataset (pd.DataFrame): Input dataset.
            target_col (str): Target column name.
            timestamp_col (str): Timestamp column name.

        Returns:
            Dict[str, Any]: Validation results with warnings and statistics.
        """
        results = {
            "valid": True,
            "warnings": [],
            "stats": {},
            "suggestions": []
        }

        # Check if columns exist
        if target_col not in dataset.columns:
            results["valid"] = False
            results["warnings"].append(f"Target column '{target_col}' not found")
            return results

        if timestamp_col not in dataset.columns:
            results["valid"] = False
            results["warnings"].append(f"Timestamp column '{timestamp_col}' not found")
            return results

        # Basic statistics
        target_data = dataset[target_col].dropna()
        results["stats"] = {
            "total_rows": len(dataset),
            "valid_values": len(target_data),
            "missing_values": len(dataset) - len(target_data),
            "date_range": {
                "start": str(dataset[timestamp_col].min()),
                "end": str(dataset[timestamp_col].max())
            },
            "target_stats": {
                "mean": float(target_data.mean()),
                "std": float(target_data.std()),
                "min": float(target_data.min()),
                "max": float(target_data.max())
            }
        }

        # Warnings and suggestions
        if len(target_data) < 30:
            results["warnings"].append("Dataset has fewer than 30 data points")
            results["suggestions"].append("Consider using more historical data for better forecasts")

        missing_pct = (len(dataset) - len(target_data)) / len(dataset) * 100
        if missing_pct > 10:
            results["warnings"].append(f"High percentage of missing values: {missing_pct:.1f}%")
            results["suggestions"].append("Consider data cleaning or imputation")

        return results


    def get_model_info(self, model_id: Optional[str] = None) -> Dict[str, str]:
        """Get information about a specific model.

        Args:
            model_id (str, optional): Model ID. If None, uses default model.

        Returns:
            Dict[str, str]: Model information.
        """
        model_id = model_id or self._client.model_id
        
        model_info = {
            "forecast-model-1": {
                "name": "Primary Forecasting Model",
                "description": "Optimized for time series prediction and trend analysis. Best for general forecasting tasks with good balance of accuracy and performance.",
                "use_cases": "General forecasting, trend analysis, business planning"
            },
            "forecast-model-2": {
                "name": "Alternative Forecasting Model", 
                "description": "Enhanced accuracy for complex patterns with multi-seasonal forecasting and anomaly detection capabilities.",
                "use_cases": "Complex seasonal patterns, anomaly detection, multi-variate analysis"
            },
            "forecast-model-3": {
                "name": "Advanced Forecasting Model",
                "description": "High-frequency data processing with real-time forecasting and scalable predictions for large datasets.",
                "use_cases": "High-frequency data, real-time forecasting, large datasets"
            },
            "forecast-model-4": {
                "name": "Next-Generation Model",
                "description": "Deep learning integration with ensemble methods and cross-domain forecasting capabilities.",
                "use_cases": "Complex patterns, cross-domain forecasting, ensemble predictions"
            }
        }
        
        if model_id not in model_info:
            raise ValueError(f"Unknown model ID: {model_id}")
        
        return model_info[model_id]

    def set_api_key(self, api_key: str, model_id: Optional[str] = None):
        """Update API key and optionally change default model.

        Args:
            api_key (str): New Nolano API key.
            model_id (str, optional): New default model ID.
        """
        self._client = NolanoClient(api_key, model_id or self._client.model_id)
        logger.info("API key updated successfully")

    def verify_api_key(self) -> Dict[str, Any]:
        """Verify the current API key with Nolano API.
        
        This method checks if the current API key is valid and has the necessary
        permissions to use the Nolano forecasting API.
        
        Returns:
            Dict[str, Any]: Verification result containing:
                - valid (bool): Whether the API key is valid
                - status (str): Status of the verification ('success', 'unauthorized', 'forbidden')
                - message (str): Human-readable message about the verification result
                
        Example:
            >>> client = Nolano(api_key="your_api_key")
            >>> result = client.verify_api_key()
            >>> if result['valid']:
            ...     print("API key is valid!")
            >>> else:
            ...     print(f"API key issue: {result['message']}")
        """
        return self._client.verify_api_key()

    def get_client(self) -> NolanoClient:
        """Get the underlying NolanoClient for advanced usage.

        Returns:
            NolanoClient: The underlying client instance.
        """
        return self._client