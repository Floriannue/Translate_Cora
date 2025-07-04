"""
updateTime - updates the time vector of a reachSet object

Syntax:
    R = updateTime(R,time)

Inputs:
    R - reachSet object
    time - new time vector

Outputs:
    R - updated reachSet object

Other m-files required: none
Subfunctions: none
MAT-files required: none

See also: reachSet
"""

from typing import TYPE_CHECKING, Union, List
import numpy as np
from cora_python.contSet.interval.interval import Interval

if TYPE_CHECKING:
    from .reachSet import ReachSet

def updateTime(R: 'ReachSet', time: Union[List, np.ndarray]) -> 'ReachSet':
    """
    Updates the time vector of a reachSet object.
    
    Args:
        R: reachSet object
        time: new time vector
        
    Returns:
        ReachSet: updated reachSet object
    """
    # Validate inputs
    if not isinstance(time, (list, np.ndarray)):
        raise ValueError("time must be a list or numpy array")
    
    # Handle single object vs list
    R_list = R if isinstance(R, list) else [R]
    
    for i in range(len(R_list)):
        R_obj = R_list[i]
        
        # Update time-point times
        if R_obj.timePoint and 'time' in R_obj.timePoint:
            if len(time) == len(R_obj.timePoint['time']):
                R_obj.timePoint['time'] = list(time)
            else:
                raise ValueError("Length of new time vector must match existing time points")
        
        # Update time-interval times if they exist
        if (R_obj.timeInterval and 'time' in R_obj.timeInterval and 
            R_obj.timeInterval['time']):
            # For time intervals, we need to be more careful about the update
            # This is a simplified implementation
            if len(time) >= len(R_obj.timeInterval['time']):
                for j in range(len(R_obj.timeInterval['time'])):
                    # Try to update interval objects
                    if hasattr(R_obj.timeInterval['time'][j], 'infimum'):
                        # Interval object - update both bounds
                        old_interval = R_obj.timeInterval['time'][j]
                        width = old_interval.supremum - old_interval.infimum
                        try:
                            R_obj.timeInterval['time'][j] = Interval(time[j], time[j] + width)
                        except ImportError:
                            R_obj.timeInterval['time'][j] = (time[j], time[j] + width)
                    else:
                        R_obj.timeInterval['time'][j] = time[j]
    
    return R_list[0] if not isinstance(R, list) else R_list
