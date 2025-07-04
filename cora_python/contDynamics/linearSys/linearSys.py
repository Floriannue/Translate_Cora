"""
linearSys - object constructor for linear time-invariant systems

This class represents linear time-invariant systems according to the following
first-order differential equations:
    x'(t) = A x(t) + B u(t) + c + E w(t)
    y(t)  = C x(t) + D u(t) + k + F v(t)

Authors: Florian Nüssel (Python implementation)
Date: 2025-06-08
"""

from typing import Optional, Union, Tuple, Any
import numpy as np
import warnings
from ..contDynamics import ContDynamics


class LinearSys(ContDynamics):
    """
    Linear time-invariant system class
    
    This class represents linear systems with the dynamics:
        x'(t) = A x(t) + B u(t) + c + E w(t)
        y(t)  = C x(t) + D u(t) + k + F v(t)
    
    where:
        x(t) ∈ R^n is the system state
        u(t) ∈ R^m is the system input  
        w(t) ∈ R^r is the disturbance
        y(t) ∈ R^q is the system output
        v(t) ∈ R^s is the output noise
    
    Attributes:
        A (np.ndarray): State matrix (n x n)
        B (np.ndarray): Input matrix (n x m)
        c (np.ndarray): Constant input (n x 1)
        C (np.ndarray): Output matrix (q x n)
        D (np.ndarray): Feedthrough matrix (q x m)
        k (np.ndarray): Output offset (q x 1)
        E (np.ndarray): Disturbance matrix (n x r)
        F (np.ndarray): Noise matrix (q x s)
        taylor (dict): Struct storing values from Taylor expansion
        krylov (dict): Struct storing values for Krylov subspace
    """
    
    def __init__(self, *args, **kwargs):
        """
        Constructor for linearSys
        
        Supports multiple calling patterns:
            LinearSys()
            LinearSys(A)
            LinearSys(A, B)
            LinearSys(A, B, c)
            LinearSys(A, B, c, C)
            LinearSys(A, B, c, C, D)
            LinearSys(A, B, c, C, D, k)
            LinearSys(A, B, c, C, D, k, E)
            LinearSys(A, B, c, C, D, k, E, F)
            LinearSys(name, A, B)
            LinearSys(name, A, B, c)
            LinearSys(name, A, B, c, C)
            LinearSys(name, A, B, c, C, D)
            LinearSys(name, A, B, c, C, D, k)
            LinearSys(name, A, B, c, C, D, k, E)
            LinearSys(name, A, B, c, C, D, k, E, F)
        
        Args:
            name (str, optional): Name of system
            A (array_like): State matrix
            B (array_like, optional): Input matrix
            c (array_like, optional): Constant input
            C (array_like, optional): Output matrix
            D (array_like, optional): Feedthrough matrix
            k (array_like, optional): Output offset
            E (array_like, optional): Disturbance matrix
            F (array_like, optional): Output disturbance matrix
        """
        # Parse input arguments
        name, A, B, c, C, D, k, E, F = self._parse_input_args(*args, **kwargs)
        
        # Check correctness of input arguments
        self._check_input_args(name, A, B, c, C, D, k, E, F, len(args))
        
        # Compute properties and set defaults
        name, A, B, c, C, D, k, E, F, states, inputs, outputs, dists, noises = \
            self._compute_properties(name, A, B, c, C, D, k, E, F)
        
        # Initialize parent class
        super().__init__(name, states, inputs, outputs, dists, noises)
        
        # Assign system matrices
        self.A = A
        self.B = B
        self.c = c
        self.C = C
        self.D = D
        self.k = k
        self.E = E
        self.F = F
        
        # Initialize internal properties (match MATLAB behavior: start as None/empty)
        self.taylor = None  # Will be initialized as TaylorLinSys when needed
        self.krylov = None
    
    
    def _parse_input_args(self, *args, **kwargs) -> Tuple[str, Any, Any, Any, Any, Any, Any, Any, Any]:
        """Parse input arguments from user and assign to variables"""
        
        # Default values
        def_name = 'linearSys'
        A = B = c = C = D = k = E = F = None
        
        # First handle positional arguments
        if len(args) > 0:
            # Check if first argument is name (string)
            if isinstance(args[0], str):
                # First argument is name
                name = args[0]
                remaining_args = args[1:]
            else:
                # No name provided, use default
                name = def_name
                remaining_args = args
            
            # Assign remaining arguments to matrices
            matrices = [A, B, c, C, D, k, E, F]
            for i, arg in enumerate(remaining_args):
                if i < len(matrices):
                    matrices[i] = arg
            A, B, c, C, D, k, E, F = matrices
        else:
            name = def_name
        
        # Then handle keyword arguments (override positional args if provided)
        if kwargs:
            name = kwargs.get('name', name)
            A = kwargs.get('A', A)
            B = kwargs.get('B', B)
            c = kwargs.get('c', c)
            # Support both 'C' and 'output_matrix' keywords
            if 'C' in kwargs:
                C = kwargs['C']
            elif 'output_matrix' in kwargs:
                C = kwargs['output_matrix']
            D = kwargs.get('D', D)
            k = kwargs.get('k', k)
            E = kwargs.get('E', E)
            F = kwargs.get('F', F)
        
        return name, A, B, c, C, D, k, E, F
    
    def _check_input_args(self, name: str, A, B, c, C, D, k, E, F, n_in: int):
        """Check correctness of input arguments"""
        
        if n_in == 0:
            return  # Empty case is valid
        
        # Check name
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        
        # Check A matrix
        if A is not None:
            A = np.asarray(A)
            if A.ndim != 2 or A.shape[0] != A.shape[1]:
                raise ValueError("State matrix A must be square")
        
        # Check other matrices if provided
        if B is not None:
            B = np.asarray(B)
            if B.ndim > 2:
                raise ValueError("Input matrix B must be 1D or 2D")
        
        if c is not None:
            c = np.asarray(c)
            if c.ndim > 1 and c.shape[1] != 1:
                raise ValueError("Offset c must be a vector")
        
        if C is not None:
            C = np.asarray(C)
            if C.ndim > 2:
                raise ValueError("Output matrix C must be 1D or 2D")
        
        if D is not None:
            D = np.asarray(D)
            if D.ndim > 2:
                raise ValueError("Feedthrough matrix D must be 1D or 2D")
        
        if k is not None:
            k = np.asarray(k)
            if k.ndim > 1 and k.shape[1] != 1:
                raise ValueError("Offset k must be a vector")
        
        if E is not None:
            E = np.asarray(E)
            if E.ndim > 2:
                raise ValueError("Disturbance matrix E must be 1D or 2D")
        
        if F is not None:
            F = np.asarray(F)
            if F.ndim > 2:
                raise ValueError("Noise matrix F must be 1D or 2D")
        
        # Check dimensional consistency if A is provided
        if A is not None:
            states = A.shape[0]
            
            # Check c dimensions
            if c is not None:
                c = np.asarray(c)
                if c.size != states:
                    raise ValueError("Length of offset c must match dimension of state matrix A")
            
            # Check B dimensions
            if B is not None:
                B = np.asarray(B)
                if B.ndim == 1:
                    if B.size != states:
                        raise ValueError("Input matrix B must have same number of rows as A")
                elif B.ndim == 2:
                    if B.shape[0] != states:
                        raise ValueError("Input matrix B must have same number of rows as A")
            
            # Check E dimensions
            if E is not None:
                E = np.asarray(E)
                if E.ndim == 1:
                    if E.size != states:
                        raise ValueError("Disturbance matrix E must have same number of rows as A")
                elif E.ndim == 2:
                    if E.shape[0] != states:
                        raise ValueError("Disturbance matrix E must have same number of rows as A")
            
            # Check C dimensions
            if C is not None:
                C = np.asarray(C)
                if C.ndim == 1:
                    if C.size != states:
                        raise ValueError("Output matrix C must have same number of columns as A")
                elif C.ndim == 2:
                    if C.shape[1] != states:
                        raise ValueError("Output matrix C must have same number of columns as A")
    
    def _compute_properties(self, name: str, A, B, c, C, D, k, E, F) -> Tuple:
        """
        Assign zero vectors/matrices for None values and compute dimensions
        """
        
        # Handle empty case
        if A is None:
            A = np.array([[]])
            states = 0
        else:
            A = np.asarray(A, dtype=float)
            states = A.shape[0]
        
        # Input matrix and number of inputs
        if A.size > 0 and B is None:
            B = np.zeros((states, 1))
        elif B is not None:
            B = np.asarray(B, dtype=float)
            if B.ndim == 1:
                B = B.reshape(-1, 1)
        
        # Handle scalar B: in MATLAB, scalar B means inputs = states
        if B is not None and B.size > 0:
            if np.isscalar(B) or (B.ndim == 0):
                inputs = states  # Scalar B means inputs = states (MATLAB behavior)
                # Convert scalar B to proper matrix: B * I (identity matrix)
                scalar_b = float(B)
                B = scalar_b * np.eye(states)
            else:
                inputs = B.shape[1] if B.ndim == 2 else 1
        else:
            inputs = 1 if states > 0 else 0
        
        # Constant offset
        if c is None:
            c = np.zeros((states, 1)) if states > 0 else np.array([[]])
        else:
            c = np.asarray(c, dtype=float)
            if c.ndim == 1:
                c = c.reshape(-1, 1)
        
        # Output matrix and number of outputs
        if C is None:
            C = np.eye(states) if states > 0 else np.array([[]])
            outputs = states
        else:
            C = np.asarray(C, dtype=float)
            if C.ndim == 1:
                C = C.reshape(1, -1)
            outputs = C.shape[0]
        
        # Feedthrough matrix
        if D is None:
            D = np.zeros((outputs, inputs)) if outputs > 0 and inputs > 0 else np.array([[]])
        else:
            D = np.asarray(D, dtype=float)
            if D.ndim == 1:
                D = D.reshape(1, -1)
            # Handle scalar D
            elif np.isscalar(D) or (D.ndim == 0):
                D = np.zeros((outputs, inputs))
        
        # Output offset
        if k is None:
            k = np.zeros((outputs, 1)) if outputs > 0 else np.array([[]])
        else:
            k = np.asarray(k, dtype=float)
            if k.ndim == 1:
                k = k.reshape(-1, 1)
        
        # Disturbance matrix and number of disturbances
        if E is None:
            E = np.zeros((states, 1)) if states > 0 else np.array([[]])
            dists = 1 if states > 0 else 0
        else:
            E = np.asarray(E, dtype=float)
            if np.isscalar(E) or (E.ndim == 0):
                # Scalar E means dists = states (MATLAB behavior)
                dists = states
                # Convert scalar E to proper matrix: E * I (identity matrix)
                scalar_e = float(E)
                E = scalar_e * np.eye(states) if states > 0 else np.array([[]])
            elif E.ndim == 1:
                E = E.reshape(-1, 1)
                dists = 1
            else:
                dists = E.shape[1]
        
        # Noise matrix and number of noises
        if F is None:
            F = np.zeros((outputs, 1)) if outputs > 0 else np.array([[]])
            noises = 1 if outputs > 0 else 0  # MATLAB behavior: when F is empty, noises = F.shape[1] = 1
        else:
            F = np.asarray(F, dtype=float)
            if np.isscalar(F) or (F.ndim == 0):
                # Scalar F means noises = outputs (MATLAB behavior)
                noises = outputs
                # Convert scalar F to proper matrix: F * I (identity matrix)
                scalar_f = float(F)
                F = scalar_f * np.eye(outputs) if outputs > 0 else np.array([[]])
            elif F.ndim == 1:
                F = F.reshape(-1, 1)
                noises = 1
            else:
                noises = F.shape[1]
        
        return name, A, B, c, C, D, k, E, F, states, inputs, outputs, dists, noises
    
    def get_taylor(self, name: str, *args):
        """
        Wrapper function to read out auxiliary values stored in sys.taylor
        If the requested value is not there, we compute it
        """
        # This is a placeholder - actual implementation would depend on 
        # the taylorLinSys class which handles Taylor expansion computations
        if name not in self.taylor:
            # Compute and store the value
            # This would call appropriate computation functions
            pass
        return self.taylor.get(name, None)
    
    def getTaylor(self, name: str, *args, **kwargs):
        """
        Wrapper function to read out auxiliary values stored in sys.taylor,
        if the requested value is not there, we compute it
        
        This method matches the MATLAB interface exactly.
        """
        from cora_python.g.classes.taylorLinSys import TaylorLinSys
        
        # Initialize taylor if not present (match MATLAB behavior)
        if self.taylor is None:
            self.taylor = TaylorLinSys(self.A)
        
        # Handle MATLAB struct-like arguments - convert dict to kwargs
        if len(args) == 1 and isinstance(args[0], dict):
            # MATLAB-style call: getTaylor(name, struct)
            struct_kwargs = args[0]
            kwargs.update(struct_kwargs)
            return self.taylor.computeField(name, **kwargs)
        else:
            # Python-style call: getTaylor(name, **kwargs)
            return self.taylor.computeField(name, *args, **kwargs)
    
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"LinearSys(name='{self.name}', A.shape={self.A.shape}, "
                f"B.shape={self.B.shape}, states={self.nr_of_dims}, "
                f"inputs={self.nr_of_inputs}, outputs={self.nr_of_outputs})")
    
 