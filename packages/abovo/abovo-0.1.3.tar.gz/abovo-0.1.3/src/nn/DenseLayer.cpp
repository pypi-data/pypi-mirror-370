#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>

#include "nn/DenseLayer.hpp"

namespace nn {

DenseLayer::DenseLayer(int in, int out, ActivationType activation)
    : input_size(in), output_size(out), weights(input_size, output_size),
      biases(1, output_size), activation_type(activation), is_quantized(false),
      quantized_weights(0, 0), quantized_biases(0, 0) {
  weights.randomize(input_size);

  for (int j = 0; j < output_size; ++j) {
    biases(0, j) = 0.0;
  }
}

void DenseLayer::quantize(bool per_channel) {
  if (!is_quantized) {
    // per_channel default
    if (per_channel) {
      quantized_weights =
          quantization::Int8Matrix::quantize_per_channel(weights);
    } else {
      quantized_weights =
          quantization::Int8Matrix::quantize_per_tensor(weights);
    }

    quantized_biases = quantization::Int8Matrix::quantize_per_tensor(biases);

    is_quantized = true;
  }
}

void DenseLayer::dequantize() {
  if (is_quantized) {
    weights = quantized_weights.dequantize();
    biases = quantized_biases.dequantize();
    is_quantized = false;
  }
}

bool DenseLayer::isQuantized() const { return is_quantized; }

void DenseLayer::simulateQuantization() {
  quantization::Int8Matrix temp_weights =
      quantization::Int8Matrix::quantize_per_channel(weights);

  quantization::Int8Matrix temp_biases =
      quantization::Int8Matrix::quantize_per_tensor(biases);

  weights = temp_weights.dequantize();
  biases = temp_biases.dequantize();
}

Matrix DenseLayer::forward(const Matrix &X) {
  last_input = X;
  Matrix z;

  if (is_quantized) {
    // dequantize and do matrix multiplication
    // will implement quantized multiplication later on
    Matrix deq_weights = quantized_weights.dequantize();
    Matrix deq_biases = quantized_biases.dequantize();
    z = X * deq_weights + deq_biases;
  } else {
    z = X * weights + biases;
  }

  last_linear_output = z;
  return z;
}

Matrix DenseLayer::activation(const Matrix &X) const {
  return Activation::activation(X, activation_type);
}

void DenseLayer::print() const {
  std::cout << "Layer: Input=" << input_size << ", Output=" << output_size
            << std::endl;
  std::cout << "Activation: " << static_cast<int>(activation_type) << std::endl;
  std::cout << "Quantized: " << (is_quantized ? "Yes" : "No") << std::endl;

  std::cout << std::endl << "Weights:" << std::endl;
  for (int i = 0; i < input_size; ++i) {
    for (int j = 0; j < output_size; ++j) {
      std::cout << weights(i, j) << " ";
    }
    std::cout << std::endl;
  }

  std::cout << std::endl << "Biases:" << std::endl;
  for (int i = 0; i < output_size; ++i) {
    std::cout << biases(0, i) << " ";
  }

  std::cout << std::endl;
}

Matrix DenseLayer::backward(const Matrix &incoming_gradient,
                            double learning_rate) {
  if (is_quantized) {
    auto saved_quantized_weights = quantized_weights;
    auto saved_quantized_biases = quantized_biases;

    weights = quantized_weights.dequantize();
    biases = quantized_biases.dequantize();
    is_quantized = false;

    Matrix result = backward(incoming_gradient, learning_rate);

    quantize();

    return result;
  }

  // z = a * W + b
  // incoming_gradient = dC_0 / da^(L)
  // last_linear_output.relu_derivative() = da^(L) / dz^(L)
  // we hadamard product it because each gradient requires an activation
  // derivative adjusted_gradient = dC_0 / da^(L) * da^(L) / dz^(L) = dC_0 /
  // dz^(L)
  Matrix activation_derivative =
      Activation::activation_derivative(last_linear_output, activation_type);

  Matrix adjusted_gradient =
      incoming_gradient.hadamard_product(activation_derivative);

  // explosion clamp
  double max_norm = 1.0;
  double current_norm = 0.0;

  for (int i = 0; i < adjusted_gradient.getRows(); ++i) {
    for (int j = 0; j < adjusted_gradient.getCols(); ++j) {
      current_norm += adjusted_gradient(i, j) * adjusted_gradient(i, j);
    }
  }
  current_norm = std::sqrt(current_norm);

  if (current_norm > max_norm) {
    double scale_factor = max_norm / current_norm;
    for (int i = 0; i < adjusted_gradient.getRows(); ++i) {
      for (int j = 0; j < adjusted_gradient.getCols(); ++j) {
        adjusted_gradient(i, j) *= scale_factor;
      }
    }
  }

  // last_input.tranpose() = dz^(L) / dw^(L)
  // grad_weights = dC_0 / dw^(L) = chain rule from other influences
  Matrix grad_weights = last_input.transpose() * adjusted_gradient;

  int adjusted_gradient_rows = adjusted_gradient.getRows();
  int adjusted_gradient_cols = adjusted_gradient.getCols();

  // dC_0 / db = dC_0 / dz * dz / db = dC_0 / dz
  Matrix grad_biases(1, adjusted_gradient_cols);
  for (int j = 0; j < adjusted_gradient_cols; ++j) {
    double sum = 0.0;
    for (int i = 0; i < adjusted_gradient_rows; ++i) {
      sum += adjusted_gradient(i, j);
    }
    grad_biases(0, j) = sum;
  }

  weights = weights + ((grad_weights * learning_rate) * -1);
  biases = biases + ((grad_biases * learning_rate) * -1);

  // pass gradient to previous layer by multiplying current gradient with
  // weights: dC_0/dz^(L) * dz^(L)/da^(L-1) = dC_0/da^(L-1)
  return adjusted_gradient * weights.transpose();
}

void DenseLayer::initializeOptimizer() {
  if (!optimizer_initialized) {
    m_weights = Matrix(input_size, output_size, 0.0);
    m_biases = Matrix(1, output_size, 0.0);
    v_weights = Matrix(input_size, output_size, 0.0);
    v_biases = Matrix(1, output_size, 0.0);
    optimizer_initialized = true;
  }
}

Matrix DenseLayer::backwardAdam(const Matrix &incoming_gradient,
                                double learning_rate, double beta1,
                                double beta2, double epsilon, int t) {
  if (is_quantized) {
    auto saved_quantized_weights = quantized_weights;
    auto saved_quantized_biases = quantized_biases;

    weights = quantized_weights.dequantize();
    biases = quantized_biases.dequantize();
    is_quantized = false;

    Matrix result = backwardAdam(incoming_gradient, learning_rate, beta1, beta2,
                                 epsilon, t);

    quantize();

    return result;
  }

  if (!optimizer_initialized) {
    initializeOptimizer();
  }

  Matrix activation_derivative =
      Activation::activation_derivative(last_linear_output, activation_type);
  Matrix adjusted_gradient =
      incoming_gradient.hadamard_product(activation_derivative);

  double max_norm = 1.0;
  double current_norm = 0.0;

  for (int i = 0; i < adjusted_gradient.getRows(); ++i) {
    for (int j = 0; j < adjusted_gradient.getCols(); ++j) {
      current_norm += adjusted_gradient(i, j) * adjusted_gradient(i, j);
    }
  }
  current_norm = std::sqrt(current_norm);

  if (current_norm > max_norm) {
    double scale_factor = max_norm / current_norm;
    for (int i = 0; i < adjusted_gradient.getRows(); ++i) {
      for (int j = 0; j < adjusted_gradient.getCols(); ++j) {
        adjusted_gradient(i, j) *= scale_factor;
      }
    }
  }

  Matrix grad_weights = last_input.transpose() * adjusted_gradient;

  Matrix grad_biases(1, adjusted_gradient.getCols());
  for (int j = 0; j < adjusted_gradient.getCols(); ++j) {
    double sum = 0.0;
    for (int i = 0; i < adjusted_gradient.getRows(); ++i) {
      sum += adjusted_gradient(i, j);
    }
    grad_biases(0, j) = sum;
  }

  for (int i = 0; i < input_size; ++i) {
    for (int j = 0; j < output_size; ++j) {
      m_weights(i, j) = beta1 * m_weights(i, j) +
                        (1 - beta1) * grad_weights(i, j); // first moment update
      v_weights(i, j) = beta2 * v_weights(i, j) +
                        (1 - beta2) * (grad_weights(i, j) *
                                       grad_weights(i, j)); // second moment

      // bias correction
      double m_corrected = m_weights(i, j) / (1 - std::pow(beta1, t));
      double v_corrected = v_weights(i, j) / (1 - std::pow(beta2, t));

      weights(i, j) -=
          learning_rate * m_corrected / (std::sqrt(v_corrected) + epsilon);
    }
  }

  for (int j = 0; j < output_size; ++j) {
    m_biases(0, j) = beta1 * m_biases(0, j) + (1 - beta1) * grad_biases(0, j);
    v_biases(0, j) = beta2 * v_biases(0, j) +
                     (1 - beta2) * (grad_biases(0, j) * grad_biases(0, j));

    double m_corrected = m_biases(0, j) / (1 - std::pow(beta1, t));
    double v_corrected = v_biases(0, j) / (1 - std::pow(beta2, t));

    biases(0, j) -=
        learning_rate * m_corrected / (std::sqrt(v_corrected) + epsilon);
  }

  return adjusted_gradient * weights.transpose();
}

} // namespace nn
