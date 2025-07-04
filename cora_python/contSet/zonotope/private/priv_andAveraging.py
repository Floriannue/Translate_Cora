"""
priv_andAveraging - computes the intersection between list of zonotopes
   according to [1]

Syntax:
    Z = priv_andAveraging(Z_cell)
    Z = priv_andAveraging(Z_cell, method)
    Z = priv_andAveraging(Z_cell, method, closedform)
    Z = priv_andAveraging(Z_cell, method, closedform, sumofw)

Inputs:
    Z_cell - list of zonotopes
    method - method to calculate weights:
             'normGen' (default)
             'volume'
             'radius'
    closedform - true/false
    sumofw - free parameter for the closed form of normGen
 
Outputs:
    Z - zonotope object enclosing the intersection

Example:
    Z1 = Zonotope(np.array([2, 1]), np.array([[2, 2], [2, 0]]))
    Z2 = Zonotope(np.array([3, 3]), np.array([[1, -1, 1], [1, 2, 0]]))
    Z = priv_andAveraging([Z1, Z2])

References:
    [1] Amr Alanwar, Jagat Jyoti Rath, Hazem Said, Matthias Althoff.
        Distributed Set-Based Observers Using Diffusion Strategy

Authors: Amr Alanwar (MATLAB)
         Python translation by AI Assistant
Written: 09-February-2020 (MATLAB)
Last update: 09-March-2020 (MATLAB), 22-March-2020 (MATLAB)
Last revision: 06-October-2024 (MATLAB, complete refactor)
Python translation: 2025
"""

import numpy as np
from typing import List, Optional
from scipy.optimize import minimize

from ..zonotope import Zonotope


def priv_andAveraging(Z_cell: List[Zonotope], 
                     method: Optional[str] = None,
                     closedform: Optional[bool] = None,
                     sumofw: Optional[float] = None) -> Zonotope:
    """
    Computes the intersection between list of zonotopes using averaging
    
    Args:
        Z_cell: List of zonotope objects
        method: Method to calculate weights ('normGen', 'volume', 'radius')
        closedform: Whether to use closed form solution (for normGen only)
        sumofw: Free parameter for the closed form of normGen
        
    Returns:
        Zonotope: Zonotope object enclosing the intersection
    """
    
    # Set default values
    if method is None:
        method = 'normGen'
    if closedform is None:
        closedform = True
    if sumofw is None:
        sumofw = 1.0
    
    # Input validation
    if not isinstance(Z_cell, list) or len(Z_cell) == 0:
        raise ValueError("Z_cell must be a non-empty list")
    
    if method not in ['normGen', 'radius', 'volume']:
        raise ValueError("method must be 'normGen', 'radius', or 'volume'")
    
    if not isinstance(closedform, bool):
        raise ValueError("closedform must be boolean")
    
    if not isinstance(sumofw, (int, float)) or sumofw < 0:
        raise ValueError("sumofw must be non-negative scalar")
    
    # Compute weighting factors
    if method == 'normGen' and closedform:
        # Analytical solution
        tVec = []
        for Z in Z_cell:
            G = Z.generators()
            tVec.append(np.trace(G @ G.T))
        
        tVec = np.array(tVec)
        inv_tVecSum = np.sum(1.0 / tVec)
        w = sumofw / (tVec * inv_tVecSum)
    
    else:
        # Find the weights via optimization
        def objective(w):
            c, G = _catWeighted(Z_cell, w)
            
            if method == 'normGen':
                return np.linalg.norm(G, 'fro')
            elif method == 'radius':
                Z_temp = Zonotope(c, G)
                return Z_temp.radius()
            elif method == 'volume':
                Z_temp = Zonotope(c, G)
                return Z_temp.volume_()
        
        # Initial guess: equal weights
        w0 = np.ones(len(Z_cell)) / len(Z_cell)
        
        # Optimization
        result = minimize(objective, w0, method='BFGS')
        w = result.x
    
    # Compute final zonotope
    c, G = _catWeighted(Z_cell, w)
    return Zonotope(c, G)


def _catWeighted(zonolist: List[Zonotope], w: np.ndarray):
    """
    Add all centers and concatenate all generator matrices from all zonotopes
    in the list, including a weighting factor
    
    Args:
        zonolist: List of zonotope objects
        w: Weight vector
        
    Returns:
        tuple: (center, generator_matrix)
    """
    n = zonolist[0].dim()
    c = np.zeros(n)
    G = np.zeros((n, 0))
    
    for i, Z in enumerate(zonolist):
        G_i = Z.generators()
        c_i = Z.center()
        
        G = np.concatenate([G, w[i] * G_i], axis=1)
        c = c + w[i] * c_i
    
    # Normalize by sum of weights
    w_sum = np.sum(w)
    c = c / w_sum
    G = G / w_sum
    
    return c, G
