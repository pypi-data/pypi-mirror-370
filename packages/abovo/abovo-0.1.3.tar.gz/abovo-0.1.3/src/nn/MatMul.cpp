#include <iostream>

#include "nn/MatMul.hpp"
#include "nn/matmul/Blocked.hpp"
#include "nn/matmul/Metal.hpp"
#include "nn/matmul/Naive.hpp"
#include "nn/matmul/SIMD.hpp"
#include "nn/matmul/SIMD_MT.hpp"

namespace nn {

Matrix matrix_multiply(const Matrix &A, const Matrix &B,
                       MatMulType type = MatMulType::NAIVE, int block_size = 64,
                       int num_threads = 0) {
  switch (type) {
  case MatMulType::NAIVE:
    return nn::matmul::multiply_naive(A, B);
  case MatMulType::BLOCKED:
    return nn::matmul::multiply_blocked(A, B, block_size);
  case MatMulType::SIMD:
    return nn::matmul::multiply_blocked_simd(A, B, block_size);
  case MatMulType::SIMD_MT:
    return nn::matmul::multiply_blocked_simd_mt(A, B, block_size, num_threads);
  case MatMulType::METAL_GPU:
    if (nn::matmul::is_metal_available()) {
      return nn::matmul::multiply_metal(A, B);
    } else {
      std::cerr << "Metal not available, falling back to blocked matrix "
                   "multiplication."
                << std::endl;
      return nn::matmul::multiply_blocked(A, B, block_size);
    }
  default:
    return nn::matmul::multiply_blocked(A, B, block_size);
  }
}

} // namespace nn