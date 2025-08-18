"""
ModelSensor - Let LLM sense the world
A Python library for detecting system information, location, time, and environment
"""

__version__ = "1.1.1"
__author__ = "EasyCam"
__email__ = "wedonotuse@outlook.com"

from .core import ModelSensor
from .formatters import JSONFormatter, MarkdownFormatter

__all__ = ["ModelSensor", "JSONFormatter", "MarkdownFormatter"] 