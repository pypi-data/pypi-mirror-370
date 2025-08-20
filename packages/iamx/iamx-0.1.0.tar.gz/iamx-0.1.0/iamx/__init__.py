"""IAM Policy Explainer - Local-first IAM policy analyzer."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.analyzer import PolicyAnalyzer
from .core.models import AnalysisResult, Finding, Severity
from .core.parser import PolicyParser

__all__ = [
    "PolicyAnalyzer",
    "AnalysisResult", 
    "Finding",
    "Severity",
    "PolicyParser",
]
