#include <stdexcept>

#include "nn/loss/MSE.hpp"

namespace nn::loss {

double mse(const Matrix &y_pred, const Matrix &y_true) {
  if (y_pred.getRows() != y_true.getRows() ||
      y_pred.getCols() != y_true.getCols()) {
    throw std::invalid_argument("Matrix dimensions must match.");
  }

  int rows = y_pred.getRows();
  int cols = y_pred.getCols();
  double sum = 0.0;
  int n = rows * cols;

  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      double diff = y_pred(i, j) - y_true(i, j);
      sum += diff * diff;
    }
  }

  return sum / n;
}

Matrix mse_derivative(const Matrix &y_pred, const Matrix &y_true) {
  if (y_pred.getRows() != y_true.getRows() ||
      y_pred.getCols() != y_true.getCols()) {
    throw std::invalid_argument("Matrix dimensions must match.");
  }

  int rows = y_pred.getRows();
  int cols = y_pred.getCols();
  int n = rows * cols;

  Matrix grad(rows, cols);

  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      grad(i, j) = 2.00 * (y_pred(i, j) - y_true(i, j)) / n;
    }
  }

  return grad;
}

} // namespace nn::loss