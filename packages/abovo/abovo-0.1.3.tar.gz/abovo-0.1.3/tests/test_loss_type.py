import unittest
import numpy as np
import _abovo
import tempfile
import os

class TestLossType(unittest.TestCase):
    def test_loss_type_enum(self):
        # Test loss type enum values
        self.assertEqual(_abovo.LossType.MSE, _abovo.LossType.MSE)
        self.assertEqual(_abovo.LossType.CrossEntropy, _abovo.LossType.CrossEntropy)
        self.assertNotEqual(_abovo.LossType.MSE, _abovo.LossType.CrossEntropy)

if __name__ == '__main__':
    unittest.main()