"""
BlackDuck - A fun blackjack variant with ducks and advanced features.

This package provides a complete blackjack game implementation with:
- Advanced features like splitting and double down
- Ace handling
- Custom "Duck" themed cards (Ducks instead of Jacks)
- ATM system for managing game currency
- Both normal and advanced game modes
"""

__version__ = "0.1.0"
__author__ = "Braeden Sy Tan"
__email__ = "braedenjairsytan@icloud.com"

from .game import main

__all__ = ["main"]
