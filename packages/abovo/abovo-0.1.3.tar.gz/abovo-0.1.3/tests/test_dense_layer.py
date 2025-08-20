import unittest
import numpy as np
import _abovo
import tempfile
import os

class TestDenseLayer(unittest.TestCase):
    def test_layer_creation(self):
        # Test with different activation functions
        layer_relu = _abovo.DenseLayer(10, 5, _abovo.ActivationType.RELU)
        layer_sigmoid = _abovo.DenseLayer(10, 5, _abovo.ActivationType.SIGMOID)
        layer_softmax = _abovo.DenseLayer(10, 5, _abovo.ActivationType.SOFTMAX)
        
        self.assertIsNotNone(layer_relu)
        self.assertIsNotNone(layer_sigmoid)
        self.assertIsNotNone(layer_softmax)
        
    def test_layer_forward(self):
        layer = _abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU)
        
        input_data = [[1.0, 2.0, 3.0]]
        input_matrix = _abovo.Matrix(input_data)
        
        # Test forward pass
        output = layer.forward(input_matrix)
        self.assertEqual(output.get_rows(), 1)
        self.assertEqual(output.get_cols(), 2)
        
    def test_layer_quantization(self):
        layer = _abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU)
        
        # Test quantization
        self.assertFalse(layer.is_quantized())
        layer.quantize(True)
        self.assertTrue(layer.is_quantized())
        
        # Test dequantization
        layer.dequantize()
        self.assertFalse(layer.is_quantized())
        
    def test_layer_print(self):
        layer = _abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU)
        layer.print()

if __name__ == '__main__':
    unittest.main()