#include <stdexcept>

#include "nn/matmul/Naive.hpp"

namespace nn::matmul {

Matrix multiply_naive(const Matrix &A, const Matrix &B) {
  if (A.getCols() != B.getRows()) {
    throw std::invalid_argument(
        "Incompatible dimensions for matrix multiplication.");
  }

  int rows = A.getRows();
  int cols = B.getCols();
  int inner = A.getCols();

  Matrix res(rows, cols);

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      double sum = 0.0;
      for (int k = 0; k < inner; ++k) {
        sum += A(i, k) * B(k, j);
      }
      res(i, j) = sum;
    }
  }

  return res;
}

} // namespace nn::matmul
