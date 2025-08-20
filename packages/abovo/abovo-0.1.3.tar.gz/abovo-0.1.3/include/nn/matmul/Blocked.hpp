#ifndef NN_MATMUL_BLOCKED_HPP
#define NN_MATMUL_BLOCKED_HPP

#include "../Matrix.hpp"

namespace nn::matmul {

Matrix multiply_blocked(const Matrix &A, const Matrix &B, int BLOCK_SIZE = 64);

}

#endif
