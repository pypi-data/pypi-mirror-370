#include "nn/matmul/SIMD.hpp"
#include <cmath>
#include <stdexcept>
#include <vector>

namespace nn::matmul {

// Basic idea: we "transpose" both matrices A and B in memory layout; then we
// can load A's columns as vectors as they are now contiguous in memory; for the
// b values we have to actually compute where they are as they aren't contiguous
// in memory and then we multiply the A columns with the b scalar values and sum
// them up; we store the result in a C block which stores them as contiguous
// vectors which we can copy over.

// Note: probably not the most efficient approach but works well for now.
Matrix multiply_blocked_simd(const Matrix &A, const Matrix &B, int BLOCK_SIZE) {
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

  std::vector<float> A_block(
      BLOCK_SIZE * BLOCK_SIZE); // buffers to convert from doubles to floats
  std::vector<float> B_block(BLOCK_SIZE * BLOCK_SIZE);
  std::vector<float> C_block(BLOCK_SIZE * BLOCK_SIZE, 0.0f); // results tile

  for (int ii = 0; ii < rows; ii += BLOCK_SIZE) {
    int block_rows = std::min(BLOCK_SIZE, rows - ii);

    for (int jj = 0; jj < cols; jj += BLOCK_SIZE) {
      int block_cols = std::min(BLOCK_SIZE, cols - jj);

      std::fill(C_block.begin(), C_block.end(),
                0.0); // similar to what we do with sum = 0

      for (int kk = 0; kk < inner; kk += BLOCK_SIZE) {
        int block_inner = std::min(BLOCK_SIZE, inner - kk);

        // Transpose in memory for faster results with SIMD
        for (int i = 0; i < block_rows; ++i) {
          for (int k = 0; k < block_inner; ++k) {
            A_block[k * BLOCK_SIZE + i] = static_cast<float>(A(ii + i, kk + k));
          }
        }

        for (int k = 0; k < block_inner; ++k) {
          for (int j = 0; j < block_cols; ++j) {
            B_block[j * BLOCK_SIZE + k] = static_cast<float>(B(kk + k, jj + j));
          }
        }

        int simd_rows = (block_rows / 4) * 4; // process as multiple of 4
        int simd_cols = (block_cols / 4) * 4;

#if defined(__ARM_NEON) || defined(__ARM_NEON__) || defined(USE_ARM_NEON)
        // ARM NEON implementation
        for (int i = 0; i < simd_rows; i += 4) {
          for (int j = 0; j < simd_cols; j += 4) {
            float32x4_t A0; // column of A

            float32x4_t C0, C1, C2, C3; // columns of C

            C0 = vld1q_f32(&C_block[(j + 0) * BLOCK_SIZE + i]);
            C1 = vld1q_f32(&C_block[(j + 1) * BLOCK_SIZE + i]);
            C2 = vld1q_f32(&C_block[(j + 2) * BLOCK_SIZE + i]);
            C3 = vld1q_f32(&C_block[(j + 3) * BLOCK_SIZE + i]);

            for (int k = 0; k < block_inner; ++k) {
              A0 = vld1q_f32(&A_block[k * BLOCK_SIZE + i]); // load column of A

              // load row elements of B
              float b0 = B_block[(j + 0) * BLOCK_SIZE + k];
              float b1 = B_block[(j + 1) * BLOCK_SIZE + k];
              float b2 = B_block[(j + 2) * BLOCK_SIZE + k];
              float b3 = B_block[(j + 3) * BLOCK_SIZE + k];

              C0 = vmlaq_n_f32(C0, A0, b0);
              C1 = vmlaq_n_f32(C1, A0, b1);
              C2 = vmlaq_n_f32(C2, A0, b2);
              C3 = vmlaq_n_f32(C3, A0, b3);
            }

            vst1q_f32(&C_block[(j + 0) * BLOCK_SIZE + i], C0);
            vst1q_f32(&C_block[(j + 1) * BLOCK_SIZE + i], C1);
            vst1q_f32(&C_block[(j + 2) * BLOCK_SIZE + i], C2);
            vst1q_f32(&C_block[(j + 3) * BLOCK_SIZE + i], C3);
          }
        }
#elif defined(__AVX__) || defined(__AVX2__)
        // x86 AVX implementation
        for (int i = 0; i < simd_rows; i += 8) {
          for (int j = 0; j < simd_cols; j += 4) {
            __m256 A0;
            __m256 C0, C1, C2, C3;

            C0 = _mm256_loadu_ps(&C_block[(j + 0) * BLOCK_SIZE + i]);
            C1 = _mm256_loadu_ps(&C_block[(j + 1) * BLOCK_SIZE + i]);
            C2 = _mm256_loadu_ps(&C_block[(j + 2) * BLOCK_SIZE + i]);
            C3 = _mm256_loadu_ps(&C_block[(j + 3) * BLOCK_SIZE + i]);

            for (int k = 0; k < block_inner; ++k) {
              A0 = _mm256_loadu_ps(&A_block[k * BLOCK_SIZE + i]);

              float b0 = B_block[(j + 0) * BLOCK_SIZE + k];
              float b1 = B_block[(j + 1) * BLOCK_SIZE + k];
              float b2 = B_block[(j + 2) * BLOCK_SIZE + k];
              float b3 = B_block[(j + 3) * BLOCK_SIZE + k];

#if defined(__AVX2__)
              C0 = _mm256_fmadd_ps(_mm256_set1_ps(b0), A0, C0);
              C1 = _mm256_fmadd_ps(_mm256_set1_ps(b1), A0, C1);
              C2 = _mm256_fmadd_ps(_mm256_set1_ps(b2), A0, C2);
              C3 = _mm256_fmadd_ps(_mm256_set1_ps(b3), A0, C3);
#else
              // For AVX but not AVX2, no FMA available
              C0 = _mm256_add_ps(C0, _mm256_mul_ps(_mm256_set1_ps(b0), A0));
              C1 = _mm256_add_ps(C1, _mm256_mul_ps(_mm256_set1_ps(b1), A0));
              C2 = _mm256_add_ps(C2, _mm256_mul_ps(_mm256_set1_ps(b2), A0));
              C3 = _mm256_add_ps(C3, _mm256_mul_ps(_mm256_set1_ps(b3), A0));
#endif
            }

            _mm256_storeu_ps(&C_block[(j + 0) * BLOCK_SIZE + i], C0);
            _mm256_storeu_ps(&C_block[(j + 1) * BLOCK_SIZE + i], C1);
            _mm256_storeu_ps(&C_block[(j + 2) * BLOCK_SIZE + i], C2);
            _mm256_storeu_ps(&C_block[(j + 3) * BLOCK_SIZE + i], C3);
          }
        }
#elif defined(__SSE__) || defined(__SSE2__) || defined(__SSE3__) ||            \
    defined(__SSSE3__) || defined(__SSE4_1__) || defined(__SSE4_2__)
        // x86 SSE implementation
        for (int i = 0; i < simd_rows; i += 4) {
          for (int j = 0; j < simd_cols; j += 4) {
            __m128 A0;
            __m128 C0, C1, C2, C3;

            C0 = _mm_loadu_ps(&C_block[(j + 0) * BLOCK_SIZE + i]);
            C1 = _mm_loadu_ps(&C_block[(j + 1) * BLOCK_SIZE + i]);
            C2 = _mm_loadu_ps(&C_block[(j + 2) * BLOCK_SIZE + i]);
            C3 = _mm_loadu_ps(&C_block[(j + 3) * BLOCK_SIZE + i]);

            for (int k = 0; k < block_inner; ++k) {
              A0 = _mm_loadu_ps(&A_block[k * BLOCK_SIZE + i]);

              float b0 = B_block[(j + 0) * BLOCK_SIZE + k];
              float b1 = B_block[(j + 1) * BLOCK_SIZE + k];
              float b2 = B_block[(j + 2) * BLOCK_SIZE + k];
              float b3 = B_block[(j + 3) * BLOCK_SIZE + k];

              C0 = _mm_add_ps(C0, _mm_mul_ps(A0, _mm_set1_ps(b0)));
              C1 = _mm_add_ps(C1, _mm_mul_ps(A0, _mm_set1_ps(b1)));
              C2 = _mm_add_ps(C2, _mm_mul_ps(A0, _mm_set1_ps(b2)));
              C3 = _mm_add_ps(C3, _mm_mul_ps(A0, _mm_set1_ps(b3)));
            }

            _mm_storeu_ps(&C_block[(j + 0) * BLOCK_SIZE + i], C0);
            _mm_storeu_ps(&C_block[(j + 1) * BLOCK_SIZE + i], C1);
            _mm_storeu_ps(&C_block[(j + 2) * BLOCK_SIZE + i], C2);
            _mm_storeu_ps(&C_block[(j + 3) * BLOCK_SIZE + i], C3);
          }
        }
#else
        // Fallback implementation for when no SIMD is available
        for (int i = 0; i < simd_rows; i += 4) {
          for (int j = 0; j < simd_cols; j += 4) {
            for (int k = 0; k < block_inner; ++k) {
              for (int ii = 0; ii < 4; ++ii) {
                float a = A_block[k * BLOCK_SIZE + i + ii];
                C_block[(j + 0) * BLOCK_SIZE + i + ii] +=
                    a * B_block[(j + 0) * BLOCK_SIZE + k];
                C_block[(j + 1) * BLOCK_SIZE + i + ii] +=
                    a * B_block[(j + 1) * BLOCK_SIZE + k];
                C_block[(j + 2) * BLOCK_SIZE + i + ii] +=
                    a * B_block[(j + 2) * BLOCK_SIZE + k];
                C_block[(j + 3) * BLOCK_SIZE + i + ii] +=
                    a * B_block[(j + 3) * BLOCK_SIZE + k];
              }
            }
          }
        }
#endif

        for (int i = 0; i < block_rows; ++i) {
          for (int j = simd_cols; j < block_cols; ++j) {
            for (int k = 0; k < block_inner; ++k) {
              C_block[j * BLOCK_SIZE + i] +=
                  A_block[k * BLOCK_SIZE + i] * B_block[j * BLOCK_SIZE + k];
            }
          }
        }

        for (int i = simd_rows; i < block_rows; ++i) {
          for (int j = 0; j < block_cols; ++j) {
            for (int k = 0; k < block_inner; ++k) {
              C_block[j * BLOCK_SIZE + i] +=
                  A_block[k * BLOCK_SIZE + i] * B_block[j * BLOCK_SIZE + k];
            }
          }
        }
      }

      for (int i = 0; i < block_rows; ++i) {
        for (int j = 0; j < block_cols; ++j) {
          res(ii + i, jj + j) =
              static_cast<double>(C_block[j * BLOCK_SIZE + i]);
        }
      }
    }
  }

  return res;
}
} // namespace nn::matmul

// Example on 2x2 matrices:

// a b   multiplied with   e f
// c d                     g h

// In memory we store as:
// a, c, b, d
// e, g, f, h
// Since calling float32x2 on column-major A will resultin a, c being loaded as
// a vector

// Result with normal dot product:
// ae + bg     af + bh
// ce + dg     cf + dh

//                                                               C_0       C_1
// iteration 1: take [a c] multiply with e, multiply with f => [ae, ce], [af,
// cf] iteration 2: take [b d] multiply with g, multiply with h => [bg, dg],
// [bh, dh] add them together                                 [ae + bg, ce +
// dg], [af + bh, cf + dh]

// C_0 has two 32-bit floating values and C_1 has two 32-bit floating values

// We do it this way since we can reuse A0 much more easily than vector-vector
// dot product and can reuse registers better.