import unittest
import numpy as np
import _abovo
import tempfile
import os

class TestMatMulType(unittest.TestCase):
    def test_matmul_type_enum(self):
        # Test activation type enum values
        self.assertEqual(_abovo.MatMulType.NAIVE, _abovo.MatMulType.NAIVE)
        self.assertEqual(_abovo.MatMulType.BLOCKED, _abovo.MatMulType.BLOCKED)
        self.assertEqual(_abovo.MatMulType.SIMD, _abovo.MatMulType.SIMD)
        self.assertEqual(_abovo.MatMulType.SIMD_MT, _abovo.MatMulType.SIMD_MT)
        # self.assertEqual(_abovo.MatMulType.METAL_GPU, _abovo.MatMulType.METAL_GPU)
        self.assertNotEqual(_abovo.MatMulType.NAIVE, _abovo.MatMulType.BLOCKED)

if __name__ == '__main__':
    unittest.main()