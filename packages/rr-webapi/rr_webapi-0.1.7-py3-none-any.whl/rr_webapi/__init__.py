"""
RaceResult Web API Python Library

A Python implementation of the RaceResult Web API, mirroring the functionality
of the Go library.
"""

from .api import API
from .public import Public
from .eventapi import EventAPI

__version__ = "1.0.0"
__all__ = ["API", "Public", "EventAPI"] 