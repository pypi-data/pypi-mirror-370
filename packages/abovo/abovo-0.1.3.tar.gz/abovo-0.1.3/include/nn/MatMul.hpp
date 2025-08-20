#ifndef NN_MATMUL_HPP
#define NN_MATMUL_HPP

#include "Matrix.hpp"

namespace nn {

enum class MatMulType {
  NAIVE = 0,
  BLOCKED = 1,
  SIMD = 2,
  SIMD_MT = 3,
  METAL_GPU = 4
};

class MatMul {
public:
  Matrix matrix_multiply(const Matrix &A, const Matrix &B,
                         MatMulType type = MatMulType::NAIVE,
                         int block_size = 64, int num_threads = 0);
};

} // namespace nn

#endif