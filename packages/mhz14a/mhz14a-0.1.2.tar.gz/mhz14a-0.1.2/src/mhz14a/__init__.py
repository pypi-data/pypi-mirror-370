"""Python library for MH-Z14A CO₂ sensor."""

from .exceptions import MHZ14AError
from .sensor import MHZ14A

__all__ = ["MHZ14A", "MHZ14AError"]
