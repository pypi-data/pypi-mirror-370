#include <stdexcept>

#include "nn/matmul/Blocked.hpp"

namespace nn::matmul {

Matrix multiply_blocked(const Matrix &A, const Matrix &B, int BLOCK_SIZE) {
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
      res(i, j) = 0.0;
    }
  }

  for (int ii = 0; ii < rows; ii += BLOCK_SIZE) {
    for (int kk = 0; kk < inner; kk += BLOCK_SIZE) {
      for (int jj = 0; jj < cols; jj += BLOCK_SIZE) {
        for (int i = ii; i < std::min(ii + BLOCK_SIZE, rows); ++i) {
          for (int k = kk; k < std::min(kk + BLOCK_SIZE, inner); ++k) {
            for (int j = jj; j < std::min(jj + BLOCK_SIZE, cols); ++j) {
              res(i, j) += A(i, k) * B(k, j);
            }
          }
        }
      }
    }
  }

  return res;
}

} // namespace nn::matmul