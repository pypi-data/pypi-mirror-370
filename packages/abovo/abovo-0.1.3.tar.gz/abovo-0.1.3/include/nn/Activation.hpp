#ifndef NN_ACTIVATION_HPP
#define NN_ACTIVATION_HPP

#include "Matrix.hpp"

namespace nn {

enum class ActivationType { RELU, LEAKY_RELU, SIGMOID, SOFTMAX };

class Activation {
public:
  static Matrix activation(const Matrix &X, ActivationType type);
  static Matrix activation_derivative(const Matrix &X, ActivationType type);
};

} // namespace nn

#endif