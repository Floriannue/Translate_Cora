"""
empty - instantiates an empty constrained zonotope

Syntax:
    cZ = empty(n)

Inputs:
    n - dimension

Outputs:
    cZ - empty conZonotope object

Other m-files required: none
Subfunctions: none
MAT-files required: none

See also: none

Authors:       Mark Wetzlinger, Tobias Ladner (MATLAB)
               Python translation by AI Assistant
Written:       09-January-2024 (MATLAB)
Python translation: 2025
"""

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .conZonotope import ConZonotope


def empty(n: int = 0) -> 'ConZonotope':
    """
    Instantiates an empty constrained zonotope
    
    Args:
        n: dimension (default: 0)
        
    Returns:
        cZ: empty conZonotope object
    """
    
    from .conZonotope import ConZonotope
    
    # Create empty center and generator matrix
    c = np.zeros((n, 1)) if n > 0 else np.zeros((0, 1))
    G = np.zeros((n, 0)) if n > 0 else np.zeros((0, 0))
    A = np.zeros((0, 0))
    b = np.zeros((0, 1))
    
    return ConZonotope(c, G, A, b) 