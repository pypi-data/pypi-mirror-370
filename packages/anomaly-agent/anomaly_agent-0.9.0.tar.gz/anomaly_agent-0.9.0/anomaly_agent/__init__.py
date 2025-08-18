"""Anomaly detection agent package for time series data analysis.

This package provides tools for detecting anomalies in time series data using
various statistical and machine learning methods.
"""

from .agent import Anomaly, AnomalyAgent, AnomalyList, AgentConfig, AgentState
from .graph import GraphManager
from .nodes import DetectionNode, VerificationNode, ErrorHandlerNode
from .plot import plot_df
from .utils import make_anomaly_config, make_df
from .streaming import StreamingProgressHandler

__version__ = "0.8.0"

__all__ = [
    "AnomalyAgent",
    "Anomaly",
    "AnomalyList",
    "AgentConfig",
    "AgentState", 
    "GraphManager",
    "DetectionNode",
    "VerificationNode",
    "ErrorHandlerNode",
    "StreamingProgressHandler",
    "plot_df",
    "make_df",
    "make_anomaly_config",
]
