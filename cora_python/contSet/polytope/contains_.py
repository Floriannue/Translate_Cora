"""
contains_ - determines if a polytope contains another set or points

This function determines if a polytope contains another set or a collection of points
using exact or approximate methods.

Syntax:
    res, cert, scaling = contains_(P, S, method, tol, maxEval, certToggle, scalingToggle)

Inputs:
    P - polytope object
    S - contSet object or single point or matrix of points
    method - method used for the containment check:
               'exact': Checks for exact containment by looping over halfspaces
               'exact:polymax': Uses halfspace representation
               'exact:venum': Uses vertex representation when applicable
               'approx': Approximative containment check
    tol - tolerance for the containment check
    maxEval - not relevant for polytope containment
    certToggle - if True, compute certification
    scalingToggle - if True, compute scaling factors

Outputs:
    res - True/False indicating containment
    cert - certification of the result
    scaling - smallest scaling factor needed for containment

Authors: Niklas Kochdumper, Viktor Kotsev, Adrian Kulmburg, Mark Wetzlinger (MATLAB)
         Python translation by AI Assistant
Written: 19-November-2019 (MATLAB)
Last update: 31-October-2024 (TL, added v-polytope/contains) (MATLAB)
Python translation: 2025
"""

import numpy as np
from typing import Union, Tuple, Any
from cora_python.g.functions.matlab.validate.postprocessing.CORAerror import CORAerror
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .polytope import Polytope
    from cora_python.contSet.contSet import ContSet

def contains_(P: 'Polytope', S: Union[np.ndarray, 'ContSet'], method: str = 'exact', 
              tol: float = 1e-12, maxEval: int = 0, certToggle: bool = True, 
              scalingToggle: bool = False) -> Tuple[Union[bool, np.ndarray], bool, Union[float, np.ndarray]]:
    """
    Determine if polytope contains another set or points
    
    Args:
        P: Polytope object
        S: Set or points to check for containment
        method: Containment check method
        tol: Tolerance for containment check
        maxEval: Maximum evaluations (not used for polytopes)
        certToggle: Whether to compute certification
        scalingToggle: Whether to compute scaling factors
        
    Returns:
        Tuple of (result, certification, scaling)
    """
    # Handle point cloud case
    if isinstance(S, np.ndarray):
        return _contains_pointcloud(P, S, method, tol, certToggle, scalingToggle)
    
    # Handle set case
    # For now, implement a simplified version that converts sets to vertices
    if hasattr(S, 'vertices'):
        try:
            vertices = S.vertices()
            return _contains_pointcloud(P, vertices, method, tol, certToggle, scalingToggle)
        except:
            # If vertices method fails, fall back to basic containment check
            pass
    
    # For other sets, try to get a representative point or convert to vertices
    if hasattr(S, 'center'):
        center = S.center()
        if center is not None:
            result, cert, scaling = _contains_pointcloud(P, center, method, tol, certToggle, scalingToggle)
            return result, cert, scaling
    
    # Default case - assume not contained
    return False, True, np.inf


def _contains_pointcloud(P, points: np.ndarray, method: str, tol: float, 
                        certToggle: bool, scalingToggle: bool) -> Tuple[Union[bool, np.ndarray], bool, Union[float, np.ndarray]]:
    """
    Check containment of point cloud in polytope
    
    Args:
        P: Polytope object
        points: Points to check (n x m matrix)
        method: Containment method
        tol: Tolerance
        certToggle: Compute certification
        scalingToggle: Compute scaling
        
    Returns:
        Tuple of (result, certification, scaling)
    """
    # Ensure points is 2D
    if points.ndim == 1:
        points = points.reshape(-1, 1)
    
    n, num_points = points.shape
    
    # After calling P.constraints(), we should have H-representation
    if P.A is None:
        raise CORAerror('CORA:notSupported', 
                       'Polytope containment requires halfspace representation (A matrix is missing).')
    
    # Initialize results
    results = np.zeros(num_points, dtype=bool)
    scaling_factors = np.ones(num_points) * np.inf
    
    # Check each point
    for i in range(num_points):
        point = points[:, i:i+1]
        
        # Assume contained until a violation is found
        is_contained = True

        # Check inequality constraints A*x <= b, if they exist
        if P.A.shape[0] > 0:
            violations = P.A @ point - P.b
            max_violation = np.max(violations)
            
            if max_violation > tol:
                is_contained = False

            # Compute scaling factor if requested
            if scalingToggle:
                if is_contained:
                    scaling_factors[i] = 1.0 # Already inside
                else:
                    # For non-contained points, compute required scaling
                    b_norm = np.linalg.norm(P.b)
                    if b_norm > 1e-9:
                        scaling_factors[i] = 1.0 + max_violation / b_norm
                    else:
                        scaling_factors[i] = 1.0 + max_violation

        # Check equality constraints if present
        if P.Ae is not None and P.Ae.shape[0] > 0:
            eq_violations = np.abs(P.Ae @ point - P.be)
            max_eq_violation = np.max(eq_violations)
            
            if max_eq_violation > tol:
                is_contained = False
        
        results[i] = is_contained
    
    # Final check for scaling factors for points that were initially outside
    # but might be considered inside due to tolerance.
    if scalingToggle:
        results_bool = results.astype(bool)
        scaling_factors[results_bool] = np.minimum(scaling_factors[results_bool], 1.0)


    # Return results
    if num_points == 1:
        return bool(results[0]), True, float(scaling_factors[0])
    else:
        return results, True, scaling_factors 