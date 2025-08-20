#include "nn/Activation.hpp"
#include "nn/activation/LeakyReLU.hpp"
#include "nn/activation/ReLU.hpp"
#include "nn/activation/Sigmoid.hpp"
#include "nn/activation/Softmax.hpp"

namespace nn {

Matrix Activation::activation(const Matrix &X, ActivationType type) {
  switch (type) {
  case ActivationType::LEAKY_RELU:
    return activation::leaky_relu(X);
  case ActivationType::SIGMOID:
    return activation::sigmoid(X);
  case ActivationType::SOFTMAX:
    return activation::softmax(X);
  default:
    return activation::relu(X);
  }
}

Matrix Activation::activation_derivative(const Matrix &X, ActivationType type) {
  switch (type) {
  case ActivationType::LEAKY_RELU:
    return activation::leaky_relu_derivative(X);
  case ActivationType::SIGMOID:
    return activation::sigmoid_derivative(X);
  case ActivationType::SOFTMAX:
    return activation::softmax_derivative(X);
  default:
    return activation::relu_derivative(X);
  }
}

} // namespace nn