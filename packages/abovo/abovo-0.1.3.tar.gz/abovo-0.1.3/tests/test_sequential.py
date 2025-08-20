import unittest
import numpy as np
import _abovo
import tempfile
import os

class TestSequential(unittest.TestCase):
    def test_sequential_creation(self):
        model = _abovo.Sequential()
        self.assertIsNotNone(model)
        
    def test_sequential_add_layer(self):
        model = _abovo.Sequential()
        layer1 = _abovo.DenseLayer(10, 5, _abovo.ActivationType.RELU)
        layer2 = _abovo.DenseLayer(5, 2, _abovo.ActivationType.SOFTMAX)
        
        model.add(layer1)
        model.add(layer2)
        
        model.print()
        
    def test_sequential_forward(self):
        model = _abovo.Sequential()
        model.add(_abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU))
        model.add(_abovo.DenseLayer(2, 1, _abovo.ActivationType.SIGMOID))
        
        input_data = [[1.0, 2.0, 3.0]]
        input_matrix = _abovo.Matrix(input_data)
        
        # Test forward pass
        output = model.forward(input_matrix)
        self.assertEqual(output.get_rows(), 1)
        self.assertEqual(output.get_cols(), 1)
        
    def test_sequential_train(self):
        model = _abovo.Sequential()
        model.add(_abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU))
        model.add(_abovo.DenseLayer(2, 1, _abovo.ActivationType.SIGMOID))
        
        X_data = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
            [10.0, 11.0, 12.0]
        ]
        y_data = [
            [0.0],
            [1.0],
            [0.0],
            [1.0]
        ]
        
        X = _abovo.Matrix(X_data)
        y = _abovo.Matrix(y_data)
        
        model.train(X, y, epochs=10, batch_size=2, learning_rate=0.01, loss_type=_abovo.LossType.MSE)
        
        # Test evaluation
        loss = model.evaluate(X, y)
        self.assertIsInstance(loss, float)
        
    @unittest.skipIf(os.environ.get('CI') == 'true', "Skipping in CI environment")
    def test_adam_optimizer(self):
        model = _abovo.Sequential()
        model.add(_abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU))
        model.add(_abovo.DenseLayer(2, 1, _abovo.ActivationType.SIGMOID))
        
        model.enable_adam(True, 0.9, 0.999, 1e-8)
        
        X = _abovo.Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        y = _abovo.Matrix([[0.0], [1.0]])
        
        model.train(X, y, epochs=5, batch_size=1, learning_rate=0.001)
        
        model.enable_adam(False)
        
    def test_qat(self):
        model = _abovo.Sequential()
        model.add(_abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU))
        model.add(_abovo.DenseLayer(2, 1, _abovo.ActivationType.SIGMOID))
        
        model.enable_qat(True)
        
        X = _abovo.Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        y = _abovo.Matrix([[0.0], [1.0]])
        
        # Train with QAT
        model.train(X, y, epochs=5, batch_size=1, learning_rate=0.01)
        
    def test_quantization(self):
        model = _abovo.Sequential()
        model.add(_abovo.DenseLayer(3, 2, _abovo.ActivationType.RELU))
        model.add(_abovo.DenseLayer(2, 1, _abovo.ActivationType.SIGMOID))
        
        # Test quantization
        model.quantize_all(True) 
        
        input_data = [[1.0, 2.0, 3.0]]
        input_matrix = _abovo.Matrix(input_data)

        output = model.forward(input_matrix)
        self.assertEqual(output.get_rows(), 1)
        self.assertEqual(output.get_cols(), 1)
        
        # Test dequantization
        model.dequantize_all()

if __name__ == '__main__':
    unittest.main()