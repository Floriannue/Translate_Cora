"""
children - return a list of indices of the children of this parent node

Syntax:
    ch = children(R, 5)

Inputs:
    R - reachSet object
    parent - index of the parent node

Outputs:
    out - list of children node indices

Other m-files required: none
Subfunctions: none
MAT-files required: none

See also: reachSet
"""

from typing import TYPE_CHECKING, List, Union
import numpy as np

if TYPE_CHECKING:
    from .reachSet import ReachSet

def children(R_list: List['ReachSet'], parent: int) -> List[int]:
    """
    Return a list of indices of the children of this parent node.
    
    Args:
        R_list: list of reachSet objects
        parent: index of the parent node
        
    Returns:
        List[int]: list of children node indices
    """
    out = []
    
    for i in range(len(R_list)):
        # Don't include the parent index itself, only its children
        if i != parent and hasattr(R_list[i], 'parent') and R_list[i].parent == parent:
            out.append(i)
    
    return out 