#include <cmath>
#include <stdexcept>

#include "nn/loss/CrossEntropy.hpp"

namespace nn::loss {

double cross_entropy(const Matrix &y_pred, const Matrix &y_true) {
  if (y_pred.getRows() != y_true.getRows() ||
      y_pred.getCols() != y_true.getCols()) {
    throw std::invalid_argument("Dimensions mismatch in cross entropy loss.");
  }

  int rows = y_pred.getRows();
  int cols = y_pred.getCols();

  double total_loss = 0.0;
  // so that we stay in a "safe zone" and don't take log(0) or log(1)
  const double epsilon = 1e-10;

  for (int i = 0; i < rows; ++i) {
    double sample_loss = 0.0;
    for (int j = 0; j < cols; ++j) {
      double stable_y_pred =
          std::max(std::min(y_pred(i, j), 1.0 - epsilon), epsilon);
      // cross entropy formula
      sample_loss += y_true(i, j) * std::log(1 / stable_y_pred);
    }
    total_loss += sample_loss;
  }

  return total_loss / rows;
}

Matrix cross_entropy_derivative(const Matrix &y_pred, const Matrix &y_true) {
  if (y_pred.getRows() != y_true.getRows() ||
      y_pred.getCols() != y_true.getCols()) {
    throw std::invalid_argument(
        "Dimensions mismatch in cross entropy derivative.");
  }

  int rows = y_pred.getRows();
  int cols = y_pred.getCols();

  Matrix grad(rows, cols);
  const double epsilon = 1e-10;

  // assume cross-entropy is used with softmax: simplifies to y_pred - y_true
  for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
      double clip_pred =
          std::max(std::min(y_pred(i, j), 1.0 - epsilon), epsilon);
      grad(i, j) = (clip_pred - y_true(i, j)) / rows;
    }
  }

  return grad;
}

} // namespace nn::loss