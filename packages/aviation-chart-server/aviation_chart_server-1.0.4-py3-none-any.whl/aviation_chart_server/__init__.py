"""
Aviation Chart Server Package

A Python service for serving FAA aviation charts as tile pyramids.
"""

__version__ = "1.0.4"
__author__ = "Roman Kozulia"
__email__ = "romanmuni8@gmail.com"

# Import main function for programmatic access
from .chart_server import main as start_server

__all__ = ["start_server"]
