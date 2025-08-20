"""
MathUtils - A simple mathematics utilities library
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main functions for easy access
from .basic_ops import add, subtract, multiply, divide, power
from .statistics import mean, median, mode, standard_deviation

# Define what gets imported with "from mathutils import *"
__all__ = [
    'add', 'subtract', 'multiply', 'divide', 'power',
    'mean', 'median', 'mode', 'standard_deviation'
]