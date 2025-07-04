"""
project - project reachable set to lower-dimensional subspace

Syntax:
    Rproj = project(R, dims)

Inputs:
    R - reachSet object
    dims - dimensions to project to

Outputs:
    Rproj - projected reachSet object

Authors: Niklas Kochdumper (MATLAB)
         Python translation by AI Assistant
Written: 02-June-2020 (MATLAB)
Last update: ---
Python translation: 2025
"""

import numpy as np
from typing import List
from .reachSet import ReachSet

def project(R, dims: List[int]):
    """
    Project reachable sets to lower-dimensional subspace
    
    Args:
        R: reachSet object
        dims: Dimensions to project to
        
    Returns:
        Projected reachSet object
        
    Raises:
        TypeError: If dims is not a valid list of integers
        ValueError: If dims contains invalid dimension indices
    """
    
    # Validate inputs
    if isinstance(dims, str):
        raise TypeError("dims must be a list of integers, not string")
    
    if not isinstance(dims, (list, tuple, np.ndarray)):
        if isinstance(dims, (int, np.integer)):
            dims = [dims]
        else:
            raise TypeError("dims must be a list of integers")
    
    dims = list(dims)
    
    # Check that all dimensions are integers
    for dim in dims:
        if not isinstance(dim, (int, np.integer)):
            raise TypeError("All dimensions must be integers")
        if dim < 0:
            raise ValueError("Dimension indices must be non-negative")
    
    # Project time-point sets
    projected_timePoint = {}
    if 'set' in R.timePoint:
        projected_timePoint['set'] = []
        for s in R.timePoint['set']:
            if hasattr(s, 'project'):
                projected_timePoint['set'].append(s.project(dims))
            else:
                # For numeric arrays, just select dimensions
                if isinstance(s, np.ndarray):
                    if s.ndim == 1:
                        projected_timePoint['set'].append(s[dims])
                    else:
                        projected_timePoint['set'].append(s[dims, :])
                else:
                    projected_timePoint['set'].append(s)
        
        # Copy other fields
        for key in ['time', 'error']:
            if key in R.timePoint:
                projected_timePoint[key] = R.timePoint[key].copy()
    
    # Project time-interval sets
    projected_timeInterval = {}
    if 'set' in R.timeInterval:
        projected_timeInterval['set'] = []
        for s in R.timeInterval['set']:
            if hasattr(s, 'project'):
                projected_timeInterval['set'].append(s.project(dims))
            else:
                # For numeric arrays, just select dimensions
                if isinstance(s, np.ndarray):
                    if s.ndim == 1:
                        projected_timeInterval['set'].append(s[dims])
                    else:
                        projected_timeInterval['set'].append(s[dims, :])
                else:
                    projected_timeInterval['set'].append(s)
        
        # Copy other fields
        for key in ['time', 'error', 'algebraic']:
            if key in R.timeInterval:
                projected_timeInterval[key] = R.timeInterval[key].copy()
    
    return ReachSet(projected_timePoint, projected_timeInterval, R.parent, R.loc) 