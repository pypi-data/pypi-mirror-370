"""
Kerykeion MCP 工具包

基于 Kerykeion 库的占星计算 MCP 服务器，提供完整的占星计算功能。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import (
    create_astrological_subject,
    get_natal_aspects,
    get_synastry_aspects,
    create_composite_chart,
    get_current_time,
)
from .server import main

__all__ = [
    "create_astrological_subject",
    "get_natal_aspects", 
    "get_synastry_aspects",
    "create_composite_chart",
    "get_current_time",
    "main",
    "__version__",
]
