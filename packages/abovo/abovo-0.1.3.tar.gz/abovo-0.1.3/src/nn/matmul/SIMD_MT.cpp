#include "nn/matmul/SIMD_MT.hpp"
#include <cmath>
#include <stdexcept>
#include <vector>

#ifndef NO_OPENMP
#ifdef _OPENMP
#include <omp.h>
#define HAVE_OPENMP 1
#endif
#endif

namespace nn::matmul {

Matrix multiply_blocked_simd_mt(const Matrix &A, const Matrix &B,
                                int BLOCK_SIZE, int num_threads) {
  if (A.getCols() != B.getRows()) {
    throw std::invalid_argument(
        "Incompatible dimensions for matrix multiplication.");
  }

  int rows = A.getRows();
  int cols = B.getCols();
  int inner = A.getCols();

#ifdef HAVE_OPENMP
  if (num_threads <= 0) {
    num_threads = omp_get_max_threads();
  }
  omp_set_num_threads(num_threads);
#endif

  Matrix res(rows, cols);

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      res(i, j) = 0.0;
    }
  }

#ifdef HAVE_OPENMP
#pragma omp parallel
#endif
  {
    std::vector<float> A_block(BLOCK_SIZE * BLOCK_SIZE);
    std::vector<float> B_block(BLOCK_SIZE * BLOCK_SIZE);
    std::vector<float> C_block(BLOCK_SIZE * BLOCK_SIZE);

#ifdef HAVE_OPENMP
#pragma omp for schedule(dynamic)
#endif
    for (int ii = 0; ii < rows; ii += BLOCK_SIZE) {
      for (int jj = 0; jj < cols; jj += BLOCK_SIZE) {
        int block_rows = std::min(BLOCK_SIZE, rows - ii);
        int block_cols = std::min(BLOCK_SIZE, cols - jj);

        std::fill(C_block.begin(), C_block.end(), 0.0);

        for (int kk = 0; kk < inner; kk += BLOCK_SIZE) {
          int block_inner = std::min(BLOCK_SIZE, inner - kk);

          for (int i = 0; i < block_rows; ++i) {
            for (int k = 0; k < block_inner; ++k) {
              A_block[k * BLOCK_SIZE + i] =
                  static_cast<float>(A(ii + i, kk + k));
            }
          }

          for (int k = 0; k < block_inner; ++k) {
            for (int j = 0; j < block_cols; ++j) {
              B_block[j * BLOCK_SIZE + k] =
                  static_cast<float>(B(kk + k, jj + j));
            }
          }

          int simd_rows = (block_rows / 4) * 4;
          int simd_cols = (block_cols / 4) * 4;

#if defined(__ARM_NEON) || defined(__ARM_NEON__) || defined(USE_ARM_NEON)
          // ARM NEON implementation
          for (int i = 0; i < simd_rows; i += 4) {
            for (int j = 0; j < simd_cols; j += 4) {
              float32x4_t A0;
              float32x4_t C0, C1, C2, C3;

              C0 = vld1q_f32(&C_block[(j + 0) * BLOCK_SIZE + i]);
              C1 = vld1q_f32(&C_block[(j + 1) * BLOCK_SIZE + i]);
              C2 = vld1q_f32(&C_block[(j + 2) * BLOCK_SIZE + i]);
              C3 = vld1q_f32(&C_block[(j + 3) * BLOCK_SIZE + i]);

              for (int k = 0; k < block_inner; ++k) {
                A0 = vld1q_f32(&A_block[k * BLOCK_SIZE + i]);

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

                C0 = _mm256_fmadd_ps(_mm256_set1_ps(b0), A0, C0);
                C1 = _mm256_fmadd_ps(_mm256_set1_ps(b1), A0, C1);
                C2 = _mm256_fmadd_ps(_mm256_set1_ps(b2), A0, C2);
                C3 = _mm256_fmadd_ps(_mm256_set1_ps(b3), A0, C3);
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

                // Use SSE multiply-add
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
  }

  return res;
}
} // namespace nn::matmul