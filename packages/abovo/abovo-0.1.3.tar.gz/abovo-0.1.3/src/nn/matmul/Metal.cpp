#include <stdexcept>
#include <iostream>

#include "nn/matmul/Metal.hpp"

#if defined(__APPLE__)
// #include <Foundation/Foundation.hpp>
// #include <Metal/Metal.hpp>
// #include <MetalPerformanceShaders/MetalPerformanceShaders.h>
// #include "metal-cpp/Metal/Metal.hpp"
// #include "metal-cpp/Foundation/Foundation.hpp"
// #include "metal-cpp/QuartzCore/QuartzCore.hpp"
#endif

namespace nn::matmul {

bool is_metal_available() {
    return false;
}

void init_metal() {
    std::cout << "Metal initialization not implemented yet" << std::endl;
}

void cleanup_metal() {
    std::cout << "Metal cleanup not implemented yet" << std::endl;
}

Matrix multiply_metal(const Matrix& A, const Matrix& B) {
    if (A.getCols() != B.getRows()) {
        throw std::invalid_argument("Incompatible dimensions for matrix multiplication.");
    }
    
    std::cout << "Metal GPU acceleration not implemented yet, falling back to naive multiplication" << std::endl;
    
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

Matrix multiply_metal_blocked(const Matrix& A, const Matrix& B, int BLOCK_SIZE) {
    return multiply_metal(A, B);
}

}