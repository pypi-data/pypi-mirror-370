#include "nn/activation/LeakyReLU.hpp"

namespace nn::activation {

Matrix leaky_relu(const Matrix &X, double alpha) {
  Matrix res(X.getRows(), X.getCols());
  for (int i = 0; i < X.getRows(); ++i) {
    for (int j = 0; j < X.getCols(); ++j) {
      res(i, j) = X(i, j) > 0 ? X(i, j) : alpha * X(i, j);
    }
  }
  return res;
}

Matrix leaky_relu_derivative(const Matrix &X, double alpha) {
  Matrix res(X.getRows(), X.getCols());
  for (int i = 0; i < X.getRows(); ++i) {
    for (int j = 0; j < X.getCols(); ++j) {
      res(i, j) = X(i, j) > 0 ? 1.0 : alpha;
    }
  }
  return res;
}

} // namespace nn::activation