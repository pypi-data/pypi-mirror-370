import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Literal


def array_split(arr: List[Any], n: int = 100) -> List[List[Any]]:
    """Split array into chunks.
    
    Args:
        arr (List[Any]): Input list or array-like object.
        n (int): Maximum chunk size. Default 100.
    
    Returns:
        List[List[Any]]: List of chunks.
    """
    for i in range(0, len(arr), n):
        yield arr[i:i + n]


def forecast_to_nolano_format(
    df: pd.DataFrame,
    timestamp_col: str,
    value_col: str
) -> Dict[str, Any]:
    """Convert pandas DataFrame to Nolano API series format.
    
    Args:
        df (pd.DataFrame): Input DataFrame with time series data
        timestamp_col (str): Column name containing timestamps
        value_col (str): Column name containing values
        
    Returns:
        Dict[str, Any]: Nolano series format with timestamps and values
        
    Raises:
        KeyError: If specified columns not found
    """
    if timestamp_col not in df.columns:
        raise KeyError(f"Timestamp column '{timestamp_col}' not found")
    
    if value_col not in df.columns:
        raise KeyError(f"Value column '{value_col}' not found")
    
    # Sort by timestamp and convert to required format
    df_sorted = df.sort_values(timestamp_col)
    timestamps = pd.to_datetime(df_sorted[timestamp_col])
    timestamp_strings = timestamps.dt.strftime('%Y-%m-%dT%H:%M:%S').tolist()
    values = df_sorted[value_col].astype(float).tolist()
    
    return {
        'timestamps': timestamp_strings,
        'values': values
    }


def nolano_forecast_to_dataframe(
    forecast_timestamps: List[str],
    lower_bound: List[float],
    median: List[float], 
    upper_bound: List[float]
) -> pd.DataFrame:
    """Convert Nolano forecast results to pandas DataFrame.
    
    Args:
        forecast_timestamps (List[str]): Forecast timestamps
        lower_bound (List[float]): Lower confidence bounds
        median (List[float]): Median forecast values
        upper_bound (List[float]): Upper confidence bounds
        
    Returns:
        pd.DataFrame: DataFrame with forecast results
        
    Raises:
        ValueError: If arrays have different lengths
    """
    lengths = [len(forecast_timestamps), len(lower_bound), len(median), len(upper_bound)]
    if not all(length == lengths[0] for length in lengths):
        raise ValueError("All forecast arrays must have the same length")
    
    return pd.DataFrame({
        'timestamp': pd.to_datetime(forecast_timestamps),
        'lower_bound': lower_bound,
        'median': median, 
        'upper_bound': upper_bound
    })



def convert_confidence_to_quantiles(confidence: float) -> List[float]:
    """Convert Nolano confidence level to Sulie quantile range.
    
    Args:
        confidence (float): Confidence level (e.g., 0.8)
        
    Returns:
        List[float]: Quantiles (e.g., [0.1, 0.9])
        
    Raises:
        ValueError: If confidence level is invalid
    """
    if not (0 < confidence < 1):
        raise ValueError("Confidence must be between 0 and 1")
    
    tail = (1 - confidence) / 2
    lower = tail
    upper = 1 - tail
    
    return [lower, upper]


def validate_nolano_series_format(series: List[Dict[str, Any]]) -> bool:
    """Validate that data is in proper Nolano series format.
    
    Args:
        series (List[Dict]): List of series objects
        
    Returns:
        bool: True if format is valid
        
    Raises:
        ValueError: If format is invalid
    """
    if not isinstance(series, list) or len(series) == 0:
        raise ValueError("Series must be a non-empty list")
    
    for i, s in enumerate(series):
        if not isinstance(s, dict):
            raise ValueError(f"Series {i} must be a dictionary")
        
        if 'timestamps' not in s or 'values' not in s:
            raise ValueError(f"Series {i} must have 'timestamps' and 'values' keys")
        
        if not isinstance(s['timestamps'], list) or not isinstance(s['values'], list):
            raise ValueError(f"Series {i}: timestamps and values must be lists")
        
        if len(s['timestamps']) != len(s['values']):
            raise ValueError(f"Series {i}: timestamps and values must have same length")
        
        if len(s['timestamps']) == 0:
            raise ValueError(f"Series {i}: must have at least one data point")
    
    return True


# ================================
# Evaluation Metrics
# ================================

def _validate_metric_inputs(actual: List[float], predicted: List[float]) -> None:
    """Validate inputs for metric calculations.
    
    Args:
        actual (List[float]): Actual observed values
        predicted (List[float]): Predicted values
        
    Raises:
        ValueError: If inputs are invalid
        TypeError: If inputs are not numeric
    """
    if not isinstance(actual, (list, np.ndarray)) or not isinstance(predicted, (list, np.ndarray)):
        raise TypeError("Both actual and predicted must be lists or numpy arrays")
    
    if len(actual) != len(predicted):
        raise ValueError(f"Length mismatch: actual ({len(actual)}) != predicted ({len(predicted)})")
    
    if len(actual) == 0:
        raise ValueError("Cannot calculate metrics on empty arrays")
    
    # Convert to numpy arrays for easier validation and computation
    actual_arr = np.array(actual, dtype=float)
    predicted_arr = np.array(predicted, dtype=float)
    
    if np.any(np.isnan(actual_arr)) or np.any(np.isnan(predicted_arr)):
        raise ValueError("Input arrays cannot contain NaN values")
    
    if np.any(np.isinf(actual_arr)) or np.any(np.isinf(predicted_arr)):
        raise ValueError("Input arrays cannot contain infinite values")


def mean_absolute_error(actual: List[float], predicted: List[float]) -> float:
    """Calculate Mean Absolute Error (MAE) between actual and predicted values.
    
    MAE measures the average magnitude of errors in predictions, giving equal weight
    to all individual differences. It's robust to outliers and easy to interpret.
    
    Formula: MAE = (1/n) * Σ|actual_i - predicted_i|
    
    Args:
        actual (List[float]): Actual observed values
        predicted (List[float]): Predicted values
        
    Returns:
        float: Mean Absolute Error
        
    Raises:
        ValueError: If inputs have different lengths or contain invalid values
        TypeError: If inputs are not numeric
        
    Example:
        >>> actual = [100, 120, 110, 130]
        >>> predicted = [95, 125, 115, 125]
        >>> mae = mean_absolute_error(actual, predicted)
        >>> print(f"MAE: {mae:.2f}")
        MAE: 5.00
    """
    _validate_metric_inputs(actual, predicted)
    
    actual_arr = np.array(actual, dtype=float)
    predicted_arr = np.array(predicted, dtype=float)
    
    mae = np.mean(np.abs(actual_arr - predicted_arr))
    return float(mae)


def weighted_absolute_percentage_error(actual: List[float], predicted: List[float]) -> float:
    """Calculate Weighted Absolute Percentage Error (WAPE) between actual and predicted values.
    
    WAPE is a measure of forecasting accuracy that weights errors by the magnitude of
    actual values. It's more robust than MAPE when actual values contain zeros or 
    are close to zero, and provides an overall percentage error across the dataset.
    
    Formula: WAPE = (Σ|actual_i - predicted_i|) / (Σ|actual_i|) * 100
    
    Args:
        actual (List[float]): Actual observed values
        predicted (List[float]): Predicted values
        
    Returns:
        float: Weighted Absolute Percentage Error as a percentage
        
    Raises:
        ValueError: If inputs have different lengths, contain invalid values, 
                   or if sum of absolute actual values is zero
        TypeError: If inputs are not numeric
        
    Example:
        >>> actual = [100, 120, 110, 130]
        >>> predicted = [95, 125, 115, 125]
        >>> wape = weighted_absolute_percentage_error(actual, predicted)
        >>> print(f"WAPE: {wape:.2f}%")
        WAPE: 4.35%
    """
    _validate_metric_inputs(actual, predicted)
    
    actual_arr = np.array(actual, dtype=float)
    predicted_arr = np.array(predicted, dtype=float)
    
    # Check for zero sum of actual values
    sum_actual = np.sum(np.abs(actual_arr))
    if sum_actual == 0:
        raise ValueError("Cannot calculate WAPE: sum of absolute actual values is zero")
    
    sum_errors = np.sum(np.abs(actual_arr - predicted_arr))
    wape = (sum_errors / sum_actual) * 100
    
    return float(wape)


def calculate_forecast_metrics(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    """Calculate multiple forecast evaluation metrics.
    
    This function computes various metrics to evaluate forecast accuracy:
    - MAE: Mean Absolute Error
    - WAPE: Weighted Absolute Percentage Error
    
    Args:
        actual (List[float]): Actual observed values
        predicted (List[float]): Predicted values
        
    Returns:
        Dict[str, float]: Dictionary containing calculated metrics
        
    Raises:
        ValueError: If inputs are invalid
        TypeError: If inputs are not numeric
        
    Example:
        >>> actual = [100, 120, 110, 130]
        >>> predicted = [95, 125, 115, 125]
        >>> metrics = calculate_forecast_metrics(actual, predicted)
        >>> print(f"MAE: {metrics['mae']:.2f}")
        >>> print(f"WAPE: {metrics['wape']:.2f}%")
        MAE: 5.00
        WAPE: 4.35%
    """
    _validate_metric_inputs(actual, predicted)
    
    return {
        'mae': mean_absolute_error(actual, predicted),
        'wape': weighted_absolute_percentage_error(actual, predicted)
    }