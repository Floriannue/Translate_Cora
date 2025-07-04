"""
times - overloaded '.*' operator for simResult objects (element-wise multiplication)

Syntax:
    simRes = simRes1 .* simRes2

Inputs:
    simRes1 - simResult object
    simRes2 - simResult object or numeric value

Outputs:
    simRes - resulting simResult object

Authors: Niklas Kochdumper (MATLAB)
         Python translation by AI Assistant
Written: 29-May-2020 (MATLAB)
Last update: ---
Python translation: 2025
"""

import numpy as np
from .simResult import SimResult

def times(simRes1, simRes2):
    """
    Overloaded '.*' operator for simResult objects (element-wise multiplication)
    
    Args:
        simRes1: First simResult object or numeric value
        simRes2: Second simResult object or numeric value
        
    Returns:
        Resulting simResult object
    """
    
    # If simRes1 is numeric and simRes2 is simResult (reverse multiplication)
    if isinstance(simRes1, (int, float, np.ndarray)) and hasattr(simRes2, 'x'):
        new_x = [x * simRes1 for x in simRes2.x]
        new_y = [y * simRes1 for y in simRes2.y] if simRes2.y else []
        new_a = [a * simRes1 for a in simRes2.a] if simRes2.a else []
        
        return SimResult(new_x, simRes2.t.copy(), simRes2.loc, new_y, new_a)
    
    # If simRes2 is numeric, multiply all states element-wise
    elif isinstance(simRes2, (int, float, np.ndarray)):
        new_x = [x * simRes2 for x in simRes1.x]
        new_y = [y * simRes2 for y in simRes1.y] if simRes1.y else []
        new_a = [a * simRes2 for a in simRes1.a] if simRes1.a else []
        
        return SimResult(new_x, simRes1.t.copy(), simRes1.loc, new_y, new_a)
    
    # If simRes2 is another simResult, this is more complex (not commonly used)
    elif hasattr(simRes2, 'x') and hasattr(simRes2, 't'):
        raise NotImplementedError("Element-wise multiplication between simResult objects not implemented")
    
    else:
        raise TypeError(f"Unsupported operand type for .*: simResult and {type(simRes2)}") 