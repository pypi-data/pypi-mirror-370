# -*- coding: utf-8 -*-
"""Test the funtion computeADOP.py"""

import pytest
import numpy as np
from LAMBDA.computeADOP import computeADOP

def test_computeADOP_1D():
    d_vec = [0.2500]
    
    expected_result = 0.5
    
    actual_result = computeADOP(d_vec)
    
    assert actual_result == expected_result
    
def test_computeADOP_2D():
    d_vec = [0.20, 0.25]
    
    expected_result = 0.472870804501588
    
    actual_result = computeADOP(d_vec)
    
    assert actual_result == pytest.approx(expected_result, rel = 1e-12)

def test_computeADOP_DUMMY():
    actual   = np.array([0.4472136, 0.5     ])
    expected = np.array([0.4472136, 0.5     ])
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=0.0)

def test_computeADOP_1Dmultiple():
    d_vec = [0.20, 0.25]
    
    expected_result = np.array([0.447213595499958, 0.5])
    
    actual_result = np.empty(2)
    actual_result[0] = computeADOP([d_vec[0]])
    actual_result[1] = computeADOP([d_vec[1]])
    
    print(actual_result-expected_result)
    
    assert np.allclose(actual_result, expected_result, rtol = 1e-12)