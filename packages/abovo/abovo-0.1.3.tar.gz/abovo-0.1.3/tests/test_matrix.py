import unittest
import numpy as np
import _abovo
import tempfile
import os

class TestMatrix(unittest.TestCase):
    def test_matrix_creation(self):
        # Test creation with dimensions
        matrix = _abovo.Matrix(3, 4)
        self.assertEqual(matrix.get_rows(), 3)
        self.assertEqual(matrix.get_cols(), 4)
        
        # Test creation with data
        data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        matrix = _abovo.Matrix(data)
        self.assertEqual(matrix.get_rows(), 2)
        self.assertEqual(matrix.get_cols(), 3)
        
    def test_matrix_access(self):
        data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        matrix = _abovo.Matrix(data)
        
        # Test getitem
        self.assertEqual(matrix[0, 0], 1.0)
        self.assertEqual(matrix[0, 2], 3.0)
        self.assertEqual(matrix[1, 1], 5.0)
        
        # Test setitem
        matrix[0, 0] = 10.0
        self.assertEqual(matrix[0, 0], 10.0)
        
    def test_matrix_operations(self):
        data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        matrix = _abovo.Matrix(data)
        
        # Test transpose
        transposed = matrix.transpose()
        self.assertEqual(transposed.get_rows(), 3)
        self.assertEqual(transposed.get_cols(), 2)
        self.assertEqual(transposed[0, 0], 1.0)
        self.assertEqual(transposed[0, 1], 4.0)
        self.assertEqual(transposed[1, 0], 2.0)
        
        # Test min/max
        self.assertEqual(matrix.get_min(), 1.0)
        self.assertEqual(matrix.get_max(), 6.0)
        
    def test_matrix_print(self):
        matrix = _abovo.Matrix(2, 2)
        matrix.print()

if __name__ == '__main__':
    unittest.main()