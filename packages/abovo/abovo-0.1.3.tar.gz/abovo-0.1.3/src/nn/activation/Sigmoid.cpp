#include <cmath>

#include "nn/activation/Sigmoid.hpp"

namespace nn::activation {

Matrix sigmoid(const Matrix &X) {
  Matrix res(X.getRows(), X.getCols());

  for (int i = 0; i < X.getRows(); ++i) {
    for (int j = 0; j < X.getCols(); ++j) {
      double x = X(i, j);
      res(i, j) = 1.0 / (1.0 + std::exp(-x));
    }
  }

  return res;
}

Matrix sigmoid_derivative(const Matrix &X) {
  Matrix res(X.getRows(), X.getCols());

  for (int i = 0; i < X.getRows(); ++i) {
    for (int j = 0; j < X.getCols(); ++j) {
      double sigmoid_x = 1.0 / (1.0 + std::exp(-X(i, j)));

      res(i, j) = sigmoid_x * (1.0 - sigmoid_x);
    }
  }

  return res;
}

} // namespace nn::activation