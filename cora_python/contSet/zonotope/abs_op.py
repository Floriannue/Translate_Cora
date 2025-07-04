import numpy as np

from .zonotope import Zonotope

def abs_op(Z: 'Zonotope') -> 'Zonotope':
    """
    Returns a zonotope with absolute values of the center and the generators.
    
    According to CORA manual Appendix A.1, this method returns a zonotope where
    all entries of the center and generator matrix are converted to their 
    absolute values.
    
    Args:
        Z: Zonotope object
        
    Returns:
        Zonotope: New zonotope with absolute values
        
    Examples:
        >>> c = np.array([[-1], [2]])
        >>> G = np.array([[2, -1], [-3, 1]])
        >>> Z = Zonotope(c, G)
        >>> Z_abs = abs_op(Z)
        >>> # Z_abs.c = [[1], [2]], Z_abs.G = [[2, 1], [3, 1]]
    """
    
    # Handle empty zonotope
    if Z.is_empty():
        return Zonotope.empty(Z.dim())
    
    # Apply absolute value to center and generators
    c_abs = np.abs(Z.c)
    G_abs = np.abs(Z.G)
    
    return Zonotope(c_abs, G_abs) 