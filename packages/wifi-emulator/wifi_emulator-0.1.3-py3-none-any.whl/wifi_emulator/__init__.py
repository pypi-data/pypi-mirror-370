"""
WiFi Emulator package
---------------------
A simple GUI tool to emulate WiFi AP/client scenarios and test WPA security.
"""

__version__ = "0.1.0"

from .gui import main, WiFi_Emulator

__all__ = ["main", "WiFi_Emulator"]
