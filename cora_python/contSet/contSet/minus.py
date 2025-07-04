"""
minus - translation of a set by a vector

This function implements subtraction for contSet objects. It handles translation
of a set by a vector and provides error handling for unsupported operations.

Authors: Mark Wetzlinger (MATLAB)
         Python translation by AI Assistant
Written: 02-May-2023 (MATLAB)
Python translation: 2025
"""

from typing import TYPE_CHECKING, Union
import numpy as np
from cora_python.g.functions.matlab.validate.postprocessing.CORAerror import CORAerror

if TYPE_CHECKING:
    from cora_python.contSet.contSet.contSet import ContSet
    
def minus(S: Union['ContSet', np.ndarray], p: Union['ContSet', np.ndarray]) -> 'ContSet':
    """
    Translation of a set by a vector
    
    Args:
        S: contSet object or numeric vector (minuend)
        p: vector or contSet object (subtrahend)
        
    Returns:
        ContSet: Result of subtraction
        
    Raises:
        CORAerror: If operation is not supported
        
    Example:
        >>> S = zonotope([1, 0], [[1, 0], [0, 1]])
        >>> p = np.array([0.5, 0.5])
        >>> result = minus(S, p)  # or result = S - p
    """
    if isinstance(p, (np.ndarray, list, tuple)) or np.isscalar(p):
        # Subtrahend is numeric, call 'plus' with negated vector
        return S.plus(-np.array(p))
    
    elif isinstance(S, (np.ndarray, list, tuple)) or np.isscalar(S):
        # Minuend is a vector, subtrahend is a set
        return S.plus(p.uminus())
    
    else:
        # Throw error for unsupported operations
        classname = type(S).__name__
        raise CORAerror('CORA:notSupported',
                       f'The function "minus" is not implemented for the class {classname} '
                       f'except for vectors as a subtrahend.\n'
                       f'If you require to compute the Minkowski difference, use "minkDiff" instead.') 