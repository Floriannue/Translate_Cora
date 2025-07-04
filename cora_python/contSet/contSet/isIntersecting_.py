"""
isIntersecting_ - checks if two sets intersect (internal use)

This function provides the internal implementation for intersection checking.
It should be overridden in subclasses to provide specific intersection logic.

Authors: Tobias Ladner (MATLAB)
         Python translation by AI Assistant
Written: 12-September-2023 (MATLAB)
Python translation: 2025
"""

from typing import TYPE_CHECKING, Union
import numpy as np
from cora_python.g.functions.matlab.validate.postprocessing.CORAerror import CORAerror

if TYPE_CHECKING:
    from cora_python.contSet.contSet.contSet import ContSet

def isIntersecting_(S1: Union['ContSet', np.ndarray], 
                    S2: Union['ContSet', np.ndarray], 
                    type_: str = 'exact',
                    tol: float = 1e-8) -> bool:
    """
    Checks if two sets intersect (internal use)
    
    This is the base implementation that throws an error. Subclasses should
    override this method to provide specific intersection checking logic.
    
    Args:
        S1: First contSet object
        S2: Second contSet object or numeric
        type_: Type of check ('exact', 'approx')
        tol: Tolerance for computation
        
    Returns:
        bool: True if sets intersect, False otherwise
        
    Raises:
        CORAerror: Always raised as this method should be overridden in subclasses
        
    Example:
        >>> # This will be overridden in specific set classes
        >>> S1 = interval([1, 2], [3, 4])
        >>> S2 = interval([2.5, 3], [4.5, 5])
        >>> result = isIntersecting_(S1, S2, 'exact')
    """
    base_class = type(S1).__bases__[0] if type(S1).__bases__ else None
    if (hasattr(type(S1), 'isIntersecting_') and 
        base_class and hasattr(base_class, 'isIntersecting_') and
        type(S1).isIntersecting_ is not base_class.isIntersecting_):
        return type(S1).isIntersecting_(S2, type_, tol)
    else:
        # This is overridden in subclass if implemented; throw error
        raise CORAerror('CORA:noops',
                       f'isIntersecting_ not implemented for {type(S1).__name__} and {type(S2).__name__} with type {type_}') 