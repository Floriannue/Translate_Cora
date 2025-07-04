# This file is part of the CORA project.
# Copyright (c) 2024, System Control and Robotics Group, TU Graz.
# All rights reserved.

import numpy as np
import pytest
from cora_python.contSet.polytope.polytope import Polytope
from cora_python.contSet.polytope.origin import origin
from cora_python.g.functions.matlab.validate.postprocessing.CORAerror import CORAerror


class TestOrigin:

    def test_origin_2d(self):
        # Test 2D origin polytope
        P = origin(2)
        
        # Check that it's a 2D polytope
        assert P.dim() == 2
        
        # Check that it's in H-representation initially
        assert P._isHRep
        assert not P._isVRep
        
        # Check halfspace representation
        expected_A = np.array([[1, 0], [0, 1], [-1, -1]])
        expected_b = np.array([[0], [0], [0]])
        assert np.array_equal(P._A, expected_A)
        assert np.array_equal(P._b, expected_b)
        
        # Trigger vertex computation and check the result
        V = P.vertices()
        assert P._isVRep
        assert V.shape == (2, 1)
        assert np.allclose(V, np.array([[0], [0]]))

    def test_origin_3d(self):
        # Test 3D origin polytope
        P = origin(3)
        
        # Check that it's a 3D polytope
        assert P.dim() == 3
        
        # Check that it's in H-representation initially
        assert P._isHRep
        assert not P._isVRep

        # Check halfspace representation
        expected_A = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, -1, -1]])
        expected_b = np.array([[0], [0], [0], [0]])
        assert np.array_equal(P._A, expected_A)
        assert np.array_equal(P._b, expected_b)

        # Trigger vertex computation and check the result
        V = P.vertices()
        assert P._isVRep
        assert V.shape == (3, 1)
        assert np.allclose(V, np.array([[0], [0], [0]]))

    def test_origin_invalid_input(self):
        # Test invalid input (non-positive dimension)
        with pytest.raises(CORAerror) as excinfo:
            origin(0)
        assert "CORA:wrongInput" in str(excinfo.value)

        with pytest.raises(CORAerror) as excinfo:
            origin(-1)
        assert "CORA:wrongInput" in str(excinfo.value)

        with pytest.raises(CORAerror) as excinfo:
            origin(1.5)
        assert "CORA:wrongInput" in str(excinfo.value) 