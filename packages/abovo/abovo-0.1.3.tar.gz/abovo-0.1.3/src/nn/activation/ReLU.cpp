#include "nn/activation/ReLU.hpp"

namespace nn::activation {

Matrix relu(const Matrix &X) {
  Matrix res(X.getRows(), X.getCols());
  for (int i = 0; i < X.getRows(); ++i) {
    for (int j = 0; j < X.getCols(); ++j) {
      res(i, j) = std::max(0.0, X(i, j));
    }
  }
  return res;
}

Matrix relu_derivative(const Matrix &X) {
  Matrix res(X.getRows(), X.getCols());
  for (int i = 0; i < X.getRows(); ++i) {
    for (int j = 0; j < X.getCols(); ++j) {
      res(i, j) = X(i, j) > 0 ? 1.0 : 0.0;
    }
  }
  return res;
}

} // namespace nn::activation