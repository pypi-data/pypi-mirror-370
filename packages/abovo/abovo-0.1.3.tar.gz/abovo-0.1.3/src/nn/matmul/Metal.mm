#include <iostream>
#include <stdexcept>

#ifdef __APPLE__
#include <Metal/Metal.h>
#include <MetalKit/MetalKit.h>
#include <Foundation/Foundation.h>
#endif

#include "nn/matmul/Metal.hpp"

namespace nn::matmul {

bool is_metal_available() { return false; }

void init_metal() {
  std::cout << "Metal initialization not implemented yet" << std::endl;
}

void cleanup_metal() {
  std::cout << "Metal cleanup not implemented yet" << std::endl;
}

Matrix multiply_metal(const Matrix &A, const Matrix &B) {
  if (A.getCols() != B.getRows()) {
    throw std::invalid_argument(
        "Incompatible dimensions for matrix multiplication.");
  }

  std::cout << "Metal GPU acceleration not implemented yet, falling back to "
               "naive multiplication"
            << std::endl;

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

Matrix multiply_metal_blocked(const Matrix &A, const Matrix &B,
                              int BLOCK_SIZE) {
  return multiply_metal(A, B);
}

} // namespace nn::matmul