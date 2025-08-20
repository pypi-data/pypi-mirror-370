#ifndef NN_MATMUL_SIMD_HPP
#define NN_MATMUL_SIMD_HPP

#if defined(__ARM_NEON) || defined(__ARM_NEON__) || defined(USE_ARM_NEON)
#include <arm_neon.h>
#elif defined(__AVX__) || defined(__AVX2__)
#include <immintrin.h>
#elif defined(__SSE__) || defined(__SSE2__) || defined(__SSE3__) ||            \
    defined(__SSSE3__) || defined(__SSE4_1__) || defined(__SSE4_2__)
#include <emmintrin.h>
#include <xmmintrin.h>
#if defined(__SSE3__)
#include <pmmintrin.h>
#endif
#if defined(__SSSE3__)
#include <tmmintrin.h>
#endif
#if defined(__SSE4_1__)
#include <smmintrin.h>
#endif
#if defined(__SSE4_2__)
#include <nmmintrin.h>
#endif
#endif

#include "../Matrix.hpp"

namespace nn::matmul {
Matrix multiply_blocked_simd(const Matrix &A, const Matrix &B,
                             int BLOCK_SIZE = 64);
}

#endif