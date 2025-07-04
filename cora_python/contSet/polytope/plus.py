from typing import Union, TYPE_CHECKING
import numpy as np
from cora_python.g.functions.matlab.validate.preprocessing import find_class_arg
from cora_python.g.functions.matlab.validate.check import equal_dim_check
from cora_python.g.functions.matlab.validate.postprocessing.CORAerror import CORAerror
from cora_python.contSet.contSet.reorder import reorder

if TYPE_CHECKING:
    from cora_python.contSet.polytope.polytope import Polytope
    from cora_python.contSet.zonotope.zonotope import Zonotope
    from cora_python.contSet.interval.interval import Interval
    from cora_python.contSet.conZonotope.conZonotope import ConZonotope
    from cora_python.contSet.zonoBundle.zonoBundle import ZonoBundle

def _aux_plus_Hpoly_Hpoly(P1: 'Polytope', P2: 'Polytope', n: int) -> 'Polytope':
    from cora_python.contSet.polytope.polytope import Polytope
    from cora_python.contSet.polytope.project import project
    
    A1, b1, Ae1, be1 = P1.A, P1.b, P1.Ae, P1.be
    A2, b2, Ae2, be2 = P2.A, P2.b, P2.Ae, P2.be

    Z_A = np.zeros((A1.shape[0], A2.shape[1]))

    A = np.block([[A2, -A2], [Z_A, A1]])
    b = np.vstack([b2, b1])
    
    # Handle equality constraints (may be None)
    if Ae1 is not None and Ae2 is not None:
        Z_Ae = np.zeros((Ae1.shape[0], Ae2.shape[1]))
        Ae = np.block([[Ae2, -Ae2], [Z_Ae, Ae1]])
        be = np.vstack([be2, be1])
        P_highdim = Polytope(A, b, Ae, be)
    elif Ae1 is not None:
        # Only P1 has equality constraints
        Z_Ae = np.zeros((Ae1.shape[0], n))
        Ae = np.block([[Z_Ae, Ae1]])
        P_highdim = Polytope(A, b, Ae, be1)
    elif Ae2 is not None:
        # Only P2 has equality constraints
        Z_Ae = np.zeros((Ae2.shape[0], n))
        Ae = np.block([[Ae2, Z_Ae]])
        P_highdim = Polytope(A, b, Ae, be2)
    else:
        # No equality constraints
        P_highdim = Polytope(A, b)

    return project(P_highdim, list(range(1, n + 1)))

def _aux_plus_Vpoly_Vpoly(P1: 'Polytope', P2: 'Polytope', n: int) -> 'Polytope':
    from cora_python.contSet.polytope.polytope import Polytope
    V1, V2 = P1.V, P2.V
    num_v1, num_v2 = V1.shape[1], V2.shape[1]
    
    # Create all combinations of vertices from V1 and V2
    V = np.zeros((n, num_v1 * num_v2))
    idx = 0
    for i in range(num_v2):
        for j in range(num_v1):
            V[:, idx] = V1[:, j] + V2[:, i]
            idx += 1
        
    return Polytope(V)

def _aux_plus_poly_point(P: 'Polytope', S: np.ndarray) -> 'Polytope':
    from cora_python.contSet.polytope.private.priv_plus_minus_vector import priv_plus_minus_vector
    from cora_python.contSet.polytope.polytope import Polytope
    if S.shape[1] > 1:
        raise CORAerror('CORA:noops', P, S)
    if S.shape[0] != P.dim():
        raise CORAerror('CORA:notSupported',
                        'Minkowski addition with scalar is not supported unless the set is 1-dimensional.')
    
    # Use H-representation if available, otherwise convert
    if P._isHRep:
        A, b, Ae, be = priv_plus_minus_vector(P._A, P._b, P._Ae, P._be, S)
        P_out = Polytope(A, b, Ae, be)
    elif P._isVRep:
        # For vertex representation, just add the vector to all vertices
        V_new = P._V + S # Broadcasting should handle this
        P_out = Polytope(V_new)
    else:
        # This case should not be reached with the new constructor
        # Force computation of H-rep and use that
        from .constraints import constraints
        P_H = constraints(P)
        A, b, Ae, be = priv_plus_minus_vector(P_H._A, P_H._b, P_H._Ae, P_H._be, S)
        P_out = Polytope(A, b, Ae, be)
        
    return P_out

def _aux_setproperties(P_out: 'Polytope', P: 'Polytope', S: Union['Polytope', np.ndarray]) -> 'Polytope':
    # In the function-based approach, we don't set properties directly.
    # Properties like boundedness and full-dimensionality will be computed 
    # on-demand when functions like isBounded() or isFullDim() are called.
    return P_out

def plus(p1: Union['Polytope', np.ndarray], p2: Union['Polytope', np.ndarray]) -> 'Polytope':
    
    p1, p2 = reorder(p1, p2)
    
    from cora_python.contSet.contSet.contSet import ContSet
    if isinstance(p2, ContSet) and p2.precedence < p1.precedence:
        return p2 + p1
        
    equal_dim_check(p1, p2)
    n = p1.dim()
    tol = 1e-10
    
    from cora_python.contSet.polytope.polytope import Polytope
    
    if isinstance(p2, Polytope):
        # Check representation flags BEFORE representsa calls that might change them
        has_v1_orig = p1._isVRep
        has_v2_orig = p2._isVRep
        has_h1_orig = p1._isHRep
        has_h2_orig = p2._isHRep
        
        # Special case checks
        if p1.representsa('fullspace', tol) or p2.representsa('fullspace', tol):
            return Polytope.Inf(n)
        if p1.representsa('emptySet', tol) or p2.representsa('emptySet', tol):
            return Polytope.empty(n)
        if p1.representsa('origin', tol):
            return p2
        if p2.representsa('origin', tol):
            return p1
        
        # Use the original representation flags for path determination
        # Prioritize V-representation over H-representation for efficiency
        if has_v1_orig and has_v2_orig:
            s_out = _aux_plus_Vpoly_Vpoly(p1, p2, n)
        elif has_h1_orig and has_h2_orig:
            s_out = _aux_plus_Hpoly_Hpoly(p1, p2, n)
        else:
            # Force conversion to H-representation
            from .constraints import constraints
            p1_H = constraints(p1)
            p2_H = constraints(p2)
            s_out = _aux_plus_Hpoly_Hpoly(p1_H, p2_H, n)
            
        return _aux_setproperties(s_out, p1, p2)
    
    # Check fullspace for non-polytope p2
    if p1.representsa('fullspace', tol) or (hasattr(p2, 'representsa') and p2.representsa('fullspace', tol)):
        return Polytope.Inf(n)
    
    if isinstance(p2, np.ndarray) and p2.ndim == 2 and p2.shape[1] == 1:
        s_out = _aux_plus_poly_point(p1, p2)
        return _aux_setproperties(s_out, p1, p2)
        
    # Other set types
    if type(p2).__name__ in ['Zonotope', 'Interval', 'ConZonotope', 'ZonoBundle']:
        s_poly = Polytope(p2)
        return p1 + s_poly
        
    raise CORAerror('CORA:noops', p1, p2) 