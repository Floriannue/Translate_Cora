"""
convHull_ - computes an enclosure for the convex hull of a zonotope and
    another set or a point

Syntax:
    Z = convHull_(Z, S)
    Z = convHull_(Z, S, method)

Inputs:
    Z - zonotope object
    S - contSet object or None
    method - method for computation (optional)

Outputs:
    Z - zonotope enclosing the convex hull

Authors: Niklas Kochdumper (MATLAB)
         Python translation by AI Assistant
Written: 26-November-2019 (MATLAB)
Last update: 29-September-2024 (MATLAB)
Python translation: 2025
"""

import numpy as np
from typing import Optional, Union, TYPE_CHECKING
from cora_python.g.functions.matlab.validate.postprocessing.CORAerror import CORAerror
from .zonotope import Zonotope

if TYPE_CHECKING:
    from cora_python.contSet.contSet import ContSet
            



def convHull_(Z: 'Zonotope', S: Optional[Union['ContSet', np.ndarray]] = None, method: str = 'exact') -> 'Zonotope':
    """
    Computes an enclosure for the convex hull of a zonotope and another set or a point
    
    Args:
        Z: Zonotope object
        S: contSet object or numeric (optional)
        method: Method for computation (default: 'exact')
        
    Returns:
        Zonotope: Zonotope enclosing the convex hull
        
    Example:
        >>> Z1 = Zonotope([2, 2], [[1, 0], [0, 1]])
        >>> Z2 = Zonotope([-2, -2], [[1, 0], [0, 1]])
        >>> Z = convHull_(Z1, Z2)
    """
    
    # Zonotope is already convex
    if S is None:
        return Z
    
    # Ensure that numeric is second input argument (reorder if necessary)
    Z_out, S = _reorder_numeric(Z, S)
    
    # Check dimensions
    if hasattr(S, 'dim') and hasattr(Z_out, 'dim'):
        if S.dim() != Z_out.dim():
            raise CORAerror('CORA:dimensionMismatch',
                          f'Dimension mismatch: {Z_out.dim()} vs {S.dim()}')
    
    # Call function with lower precedence if applicable
    if hasattr(S, 'precedence') and hasattr(Z_out, 'precedence') and S.precedence < Z_out.precedence:
        return S.convHull(Z_out, method)
    
    # Convex hull with empty set
    # Only check representsa_ for objects that have the necessary methods
    if hasattr(S, '__class__') and hasattr(S, 'isemptyobject') and S.representsa_('emptySet', 1e-15):
        return Z_out
    elif Z_out.representsa_('emptySet', 1e-15):
        return S if isinstance(S, Zonotope) else Zonotope(S, np.array([]).reshape(len(S), 0))
    
    # Use enclose method
    if isinstance(S, Zonotope):
        S_zono = S
    else:
        # Convert S to zonotope
        S_zono = Zonotope(S)
    
    return Z_out.enclose(S_zono)


def _reorder_numeric(Z, S):
    """
    Ensure that numeric is second input argument
    
    Args:
        Z: First operand
        S: Second operand
        
    Returns:
        tuple: (zonotope_operand, other_operand) with zonotope first
    """
    
    # Check for zonotope using both isinstance and class name for robustness
    Z_is_zonotope = isinstance(Z, Zonotope) or (hasattr(Z, '__class__') and Z.__class__.__name__ == 'Zonotope')
    S_is_zonotope = isinstance(S, Zonotope) or (hasattr(S, '__class__') and S.__class__.__name__ == 'Zonotope')
    
    if Z_is_zonotope:
        return Z, S
    elif S_is_zonotope:
        return S, Z
    else:
        # Both are numeric, return as is
        return Z, S 