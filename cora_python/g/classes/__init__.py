"""
Classes package - Global classes for CORA

This package contains all global classes used throughout CORA.
"""

# Import classes from their respective packages
from .reachSet import ReachSet
from .simResult import SimResult
from .taylorLinSys import TaylorLinSys
from .linErrorBound import LinErrorBound
from .verifyTime import VerifyTime
from .setproperty import SetProperty
from .initialSet import InitialSet
from .intKaucher import IntKaucher
from .testCase import CoraTestCase

# Export all classes
__all__ = [
    'ReachSet',
    'SimResult', 
    'TaylorLinSys',
    'LinErrorBound',
    'VerifyTime',
    'SetProperty',
    'InitialSet',
    'IntKaucher',
    'CoraTestCase',
] 