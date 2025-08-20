"""
FHIL Python Utils - Root package for backward compatibility.

This file imports everything from the src package to maintain compatibility
with existing code that imports directly from the root.
"""

# Import everything from the src package
from src.FHIL_python_utils import *

# Also make the package itself available
import src.FHIL_python_utils as FHIL_python_utils
