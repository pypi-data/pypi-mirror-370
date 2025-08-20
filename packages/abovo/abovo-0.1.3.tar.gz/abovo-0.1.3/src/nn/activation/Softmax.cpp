#include <cmath>

#include "nn/activation/Softmax.hpp"

namespace nn::activation {

Matrix softmax(const Matrix &X) {

  int rows = X.getRows();
  int cols = X.getCols();

  Matrix res(rows, cols);

  for (int i = 0; i < rows; ++i) {
    // finding max for numerical stability
    double max = X(i, 0);
    for (int j = 1; j < cols; ++j) {
      max = std::max(max, X(i, j));
    }

    std::vector<double> exp_vals(cols);
    double exp_sum = 0.0;

    for (int j = 0; j < cols; ++j) {
      double exp_val = std::exp(X(i, j) - max);
      exp_vals[j] = exp_val;
      exp_sum += exp_val;
    }

    // normalize
    for (int j = 0; j < cols; ++j) {
      res(i, j) = exp_vals[j] / exp_sum;
    }
  }

  return res;
}

Matrix softmax_derivative(const Matrix &X) {
  int rows = X.getRows();
  int cols = X.getCols();

  // placeholder
  // assume we always use softmax with cross-entropy loss
  Matrix res(rows, cols, 1.0);

  return res;
}

} // namespace nn::activation