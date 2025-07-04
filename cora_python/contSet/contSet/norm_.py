"""
norm_ - compute the norm of a set (internal use)

This function provides the internal implementation for norm computation.
It should be overridden in subclasses to provide specific norm computation logic.

Authors: Tobias Ladner (MATLAB)
         Python translation by AI Assistant
Written: 12-September-2023 (MATLAB)
Python translation: 2025
"""

from typing import TYPE_CHECKING, Union, Tuple
import numpy as np
from cora_python.g.functions.matlab.validate.postprocessing.CORAerror import CORAerror

if TYPE_CHECKING:
    from cora_python.contSet.contSet.contSet import ContSet

def norm_(S: 'ContSet', norm_type: Union[int, float, str] = 2, mode: str = 'ub') -> Union[float, Tuple[float, np.ndarray]]:
    """
    Compute the norm of a set (internal use, see also contSet/norm)
    
    This is the base implementation that throws an error. Subclasses should
    override this method to provide specific norm computation logic.
    
    Args:
        S: contSet object
        norm_type: Type of norm to compute
        mode: Mode for computation
        
    Returns:
        Union[float, Tuple[float, np.ndarray]]: Norm value or tuple of (norm, point)
        
    Raises:
        CORAerror: Always raised as this method should be overridden in subclasses
        
    Example:
        >>> # This will be overridden in specific set classes
        >>> S = interval([1, 2], [3, 4])
        >>> norm_val = norm_(S, 2, 'ub')
    """
    base_class = type(S).__bases__[0] if type(S).__bases__ else None
    if (hasattr(type(S), 'norm_') and 
        base_class and hasattr(base_class, 'norm_') and
        type(S).norm_ is not base_class.norm_):
        return type(S).norm_(norm_type, mode)
    else:
        # This is overridden in subclass if implemented; throw error
        raise CORAerror('CORA:noops',
                    f'norm_ not implemented for {type(S).__name__} with norm_type {norm_type} and mode {mode}') 