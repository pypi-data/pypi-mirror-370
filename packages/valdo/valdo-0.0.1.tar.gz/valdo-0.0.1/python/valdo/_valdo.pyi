from typing import List, Optional, Tuple
from enum import Enum

__version__: str

class AnomalyStatus(Enum):
    """Enumeration representing the result of anomaly detection."""
    Normal: "AnomalyStatus"
    Anomaly: "AnomalyStatus"
    
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class Detector:
    """
    Valdo anomaly detector for time series data.
    
    Uses a cascaded smoothing approach with EWMA residual prediction,
    standard deviation fluctuation estimation, and SPOT anomaly detection.
    """
    
    def __init__(
        self,
        window_size: int,
        quantile: Optional[float] = None,
        level: Optional[float] = None,
        max_excess: Optional[int] = None,
    ) -> None:
        """
        Create a new Detector with specified window size and optional parameters.
        
        Args:
            window_size: Size of the sliding window for processing
            quantile: Quantile parameter for SPOT detector (default: 0.0001)
            level: Level parameter for SPOT detector (default: 0.998)
            max_excess: Maximum excess for SPOT detector (default: 200)
        
        Raises:
            ValueError: If detector creation fails
        """
        ...
    
    def train(
        self,
        data: List[Tuple[int, float]],
    ) -> None:
        """
        Train the detector on historical data.
        
        Args:
            data: List of (timestamp, value) pairs
        
        Raises:
            ValueError: If training fails
        """
        ...
    
    def detect(self, timestamp: int, value: float) -> AnomalyStatus:
        """
        Detect anomalies in a new data point.
        
        Args:
            timestamp: Timestamp of the data point
            value: Value of the data point
        
        Returns:
            AnomalyStatus: Normal or Anomaly
        
        Raises:
            ValueError: If detection fails
        """
        ...
