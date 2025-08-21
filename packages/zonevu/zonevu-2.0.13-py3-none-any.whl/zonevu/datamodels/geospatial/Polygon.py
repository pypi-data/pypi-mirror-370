"""
Polygon geometry.

Defines an outer ring and optional holes.
"""

from dataclasses import dataclass
from .Polyline import Polyline


@dataclass
class Polygon(Polyline):
    """
    Same as Polyline but known to be closed.
    """
    pass
