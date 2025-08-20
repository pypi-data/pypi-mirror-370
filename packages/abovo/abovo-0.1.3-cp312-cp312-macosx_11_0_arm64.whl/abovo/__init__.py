"""
Abovo: A C++ neural network engine with Python bindings for educational performance optimization.
"""

__version__ = "0.1.3"

from _abovo import (
    Matrix as _Matrix,
    DenseLayer as _DenseLayer,
    Sequential as _Sequential,
    LossType,
    ActivationType,
    MatMulType,
)

class Matrix(_Matrix):
    """
    A 2D matrix supporting basic operations like transpose, min/max lookup, and element access.

    Args:
        rows (int): Number of rows.
        cols (int): Number of columns.
    """

    def get_rows(self) -> int:
        """Returns the number of rows in the matrix."""
        return super().get_rows()

    def get_cols(self) -> int:
        """Returns the number of columns in the matrix."""
        return super().get_cols()

    def transpose(self) -> "Matrix":
        """Returns a new matrix that is the transpose of this one."""
        return super().transpose()

    def get_min(self) -> float:
        """Returns the minimum value in the matrix."""
        return super().get_min()

    def get_max(self) -> float:
        """Returns the maximum value in the matrix."""
        return super().get_max()

    def print(self):
        """Prints the matrix to stdout."""
        return super().print()


class DenseLayer(_DenseLayer):
    """
    A fully connected neural network layer with optional quantization and activation.

    Args:
        input_size (int): Number of input features.
        output_size (int): Number of output features.
        activation (ActivationType): Activation function to apply.
    """

    def forward(self, input: Matrix) -> Matrix:
        """Performs a forward pass through the layer."""
        return super().forward(input)

    def quantize(self):
        """Quantizes the layer weights (useful for efficient inference)."""
        return super().quantize()

    def dequantize(self):
        """Dequantizes the layer weights."""
        return super().dequantize()

    def is_quantized(self) -> bool:
        """Returns whether the layer is currently quantized."""
        return super().is_quantized()

    def print(self):
        """Prints the layer's weights and configuration."""
        return super().print()


class Sequential(_Sequential):
    """
    A sequential model for stacking layers and training.

    Methods:
        add(layer): Add a DenseLayer to the model.
        forward(X): Perform a forward pass.
        train(...): Train the model with given parameters.
        evaluate(...): Evaluate model accuracy.
        quantize_all(): Quantize all layers.
        dequantize_all(): Revert quantization.
        enable_qat(): Enable quantization-aware training.
        enable_adam(...): Use Adam optimizer.
    """

    def add(self, layer: DenseLayer):
        """Adds a new DenseLayer to the model."""
        return super().add(layer)

    def forward(self, X: Matrix) -> Matrix:
        """Feeds input X through the model and returns the output."""
        return super().forward(X)

    def train(self, X, y, epochs, batch_size, learning_rate, loss_type=LossType.MSE):
        """
        Trains the model on data using gradient descent.

        Args:
            X (Matrix): Input data.
            y (Matrix): Target labels.
            epochs (int): Number of training epochs.
            batch_size (int): Batch size.
            learning_rate (float): Learning rate.
            loss_type (LossType): Loss function to use.
        """
        return super().train(X, y, epochs, batch_size, learning_rate, loss_type)

    def evaluate(self, X, y):
        """Evaluates model performance on test data."""
        return super().evaluate(X, y)

    def quantize_all(self, per_channel=True):
        """Quantizes all layers in the model."""
        return super().quantize_all(per_channel)

    def dequantize_all(self):
        """Dequantizes all layers."""
        return super().dequantize_all()

    def enable_qat(self):
        """Enables quantization-aware training."""
        return super().enable_qat()

    def enable_adam(self, enable=True, beta1=0.9, beta2=0.999, epsilon=1e-8):
        """
        Enables Adam optimizer with given hyperparameters.

        Args:
            enable (bool): Whether to use Adam.
            beta1 (float): Exponential decay rate for 1st moment.
            beta2 (float): Exponential decay rate for 2nd moment.
            epsilon (float): Small value to avoid division by zero.
        """
        return super().enable_adam(enable, beta1, beta2, epsilon)

    def print(self):
        """Prints the model structure and parameters."""
        return super().print()


__all__ = [
    "Matrix",
    "DenseLayer",
    "Sequential",
    "LossType",
    "ActivationType",
    "MatMulType",
]
