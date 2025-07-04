"""
priv_box_H - computes the halfspace representation of the box enclosure
    given a halfspace representation

Syntax:
    A, b, empty = priv_box_H(A, b, Ae, be, n)

Inputs:
    A - inequality constraint matrix
    b - inequality constraint offset
    Ae - equality constraint matrix
    be - equality constraint offset
    n - dimension of polytope

Outputs:
    A - inequality constraint matrix
    b - inequality constraint offset
    empty - true/false whether result is the empty set
    fullDim - true/false on degeneracy
    bounded - true/false on boundedness

Other m-files required: none
Subfunctions: none
MAT-files required: none

See also: none

Authors: Mark Wetzlinger (MATLAB)
         Python translation by AI Assistant
Written: 03-October-2024 (MATLAB)
Python translation: 2025
"""

import numpy as np
from typing import Tuple
from cora_python.g.functions.matlab.init import unitvector
from .priv_supportFunc import priv_supportFunc


def priv_box_H(A: np.ndarray, b: np.ndarray, Ae: np.ndarray, be: np.ndarray, 
               n: int) -> Tuple[np.ndarray, np.ndarray, bool]:
    """
    Computes the halfspace representation of the box enclosure
    given a halfspace representation
    
    Args:
        A: Inequality constraint matrix
        b: Inequality constraint offset
        Ae: Equality constraint matrix
        be: Equality constraint offset
        n: Dimension of polytope
        
    Returns:
        tuple: (A, b, empty) where:
            A - inequality constraint matrix
            b - inequality constraint offset
            empty - true/false whether result is the empty set
    """
    
    # init bounds
    ub = np.full((n, 1), np.inf)
    lb = np.full((n, 1), -np.inf)
    
    # loop over all 2n positive/negative basis vectors
    for i in range(n):
        # i-th basis vector (using 0-based indexing)
        e_i = unitvector(i + 1, n)  # unitvector uses 1-based indexing
        
        # maximize
        ub_val, _ = priv_supportFunc(A, b, Ae, be, e_i, 'upper')
        ub[i, 0] = ub_val
        if ub[i, 0] == -np.inf:
            empty = True
            A_out = np.array([]).reshape(0, n)
            b_out = np.array([]).reshape(0, 1)
            return A_out, b_out, empty
        
        # minimize
        lb_val, _ = priv_supportFunc(A, b, Ae, be, e_i, 'lower')
        lb[i, 0] = lb_val
    
    # construct output arguments
    A_out = np.vstack([np.eye(n), -np.eye(n)])
    b_out = np.vstack([ub, -lb])
    
    # emptiness
    empty = False
    
    return A_out, b_out, empty 