"""
Visualization module for Expert Scorecards.

This module provides interactive Plotly-based visualizations for expert scorecards,
including scorecard overviews, feature analysis, and scoring simulations.

Note: This module requires plotly. Install with: pip install risk-kit[viz]
"""

from .visualiser import ScorecardVisualizer

__all__ = ["ScorecardVisualizer"]
