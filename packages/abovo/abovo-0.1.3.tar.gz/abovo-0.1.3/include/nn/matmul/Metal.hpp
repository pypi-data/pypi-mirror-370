#ifndef NN_MATMUL_METAL_HPP
#define NN_MATMUL_METAL_HPP

#include "../Matrix.hpp"

namespace nn::matmul {
Matrix multiply_metal(const Matrix &A, const Matrix &B);
Matrix multiply_metal_blocked(const Matrix &A, const Matrix &B,
                              int BLOCK_SIZE = 64);
bool is_metal_available();

void init_metal();
void cleanup_metal();
} // namespace nn::matmul

#endif
