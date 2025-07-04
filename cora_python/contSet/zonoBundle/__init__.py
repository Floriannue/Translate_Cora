"""
ZonoBundle package - Zonotope bundles

This package provides the ZonoBundle class and all its methods.
Each method is implemented in a separate file following the MATLAB structure.

Authors: Matthias Althoff, Niklas Kochdumper, Mark Wetzlinger (MATLAB)
         Python translation by AI Assistant
"""

# Import the main ZonoBundle class
from .zonoBundle import ZonoBundle

# Import method implementations that exist
from .dim import dim
from .isemptyobject import isemptyobject
from .empty import empty
from .origin import origin
from .generateRandom import generateRandom

# Attach methods to the ZonoBundle class
# dim and isemptyobject are required by ContSet
ZonoBundle.dim = dim
ZonoBundle.isemptyobject = isemptyobject

# Attach static methods
ZonoBundle.empty = staticmethod(empty)
ZonoBundle.origin = staticmethod(origin)
ZonoBundle.generateRandom = staticmethod(generateRandom)

# Export the ZonoBundle class and all methods
__all__ = [
    'ZonoBundle',
    'dim',
    'isemptyobject',
    'empty',
    'origin',
    'generateRandom',
] 