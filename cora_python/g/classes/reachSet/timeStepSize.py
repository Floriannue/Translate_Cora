"""
timeStepSize - returns time step size for the reachable set

Syntax:
    [dt,uniform,hybrid] = timeStepSize(R)

Inputs:
    R - reachSet object

Outputs:
    dt - time step size (scalar or vector)
    uniform - uniform time step size (true) or not (false)
    hybrid - reachable set belongs to a hybrid system

Other m-files required: none
Subfunctions: none
MAT-files required: none

See also: reachSet
"""

from typing import TYPE_CHECKING, Tuple, Union
import numpy as np

if TYPE_CHECKING:
    from .reachSet import ReachSet

def timeStepSize(R: 'ReachSet') -> Tuple[Union[float, np.ndarray], bool, bool]:
    """
    Returns time step size for the reachable set.
    
    Args:
        R: reachSet object
        
    Returns:
        Tuple containing:
        - dt: time step size (scalar or vector)
        - uniform: uniform time step size (True) or not (False)
        - hybrid: reachable set belongs to a hybrid system
    """
    # Handle single object vs list
    R_list = R if isinstance(R, list) else [R]
    
    # initialization
    hybrid = False
    uniform = False
    dt = []
    
    # loop over all reachable set objects
    for i in range(len(R_list)):
        R_obj = R_list[i]
        
        if not R_obj.timePoint or 'time' not in R_obj.timePoint or not R_obj.timePoint['time']:
            continue
            
        times = R_obj.timePoint['time']
        
        # check if times are intervals or scalar values
        numeric_times = []
        
        for time_val in times:
            if isinstance(time_val, (int, float)):
                numeric_times.append(time_val)
            elif hasattr(time_val, 'infimum'):
                # Interval object
                numeric_times.append(time_val.infimum)
                hybrid = True
            elif hasattr(time_val, 'inf'):
                # Alternative interval representation
                numeric_times.append(time_val.inf)
                hybrid = True
            else:
                # Try to convert to float
                try:
                    numeric_times.append(float(time_val))
                except:
                    # Skip non-numeric values
                    continue
        
        if len(numeric_times) > 1:
            # Calculate time differences
            time_diffs = np.diff(numeric_times)
            dt.extend(time_diffs)
    
    # Convert to numpy array
    dt = np.array(dt)
    
    # check if time step is uniform
    if len(dt) > 0 and np.all(np.abs(np.diff(dt)) < 1e-10):
        uniform = True
        dt = dt[0]  # Return scalar for uniform time step
    
    return dt, uniform, hybrid
