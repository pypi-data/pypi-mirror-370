import unittest
import numpy as np
import _abovo
import tempfile
import os

class TestActivationType(unittest.TestCase):
    def test_activation_type_enum(self):
        # Test activation type enum values
        self.assertEqual(_abovo.ActivationType.RELU, _abovo.ActivationType.RELU)
        self.assertEqual(_abovo.ActivationType.SIGMOID, _abovo.ActivationType.SIGMOID)
        self.assertEqual(_abovo.ActivationType.SOFTMAX, _abovo.ActivationType.SOFTMAX)
        self.assertEqual(_abovo.ActivationType.LEAKY_RELU, _abovo.ActivationType.LEAKY_RELU)
        self.assertNotEqual(_abovo.ActivationType.RELU, _abovo.ActivationType.SIGMOID)

if __name__ == '__main__':
    unittest.main()