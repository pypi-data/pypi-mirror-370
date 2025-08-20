#ifndef NN_INT8MATRIX_HPP
#define NN_INT8MATRIX_HPP

#include "../Matrix.hpp"
#include <cstddef>
#include <cstdint>
#include <vector>

namespace nn::quantization {

class Int8Matrix {
public:
  size_t rows;
  size_t cols;
  std::vector<int8_t> data;

  std::vector<float> scales;
  std::vector<float> zeros;
  bool per_channel;

  Int8Matrix(size_t rows, size_t cols);                          // channel
  Int8Matrix(size_t rows, size_t cols, float scale, float zero); // tensor

  int8_t &operator()(size_t i, size_t j);
  const int8_t &operator()(size_t i, size_t j) const;

  static Int8Matrix quantize_per_tensor(const nn::Matrix &X);
  static Int8Matrix quantize_per_channel(const nn::Matrix &X);
  nn::Matrix dequantize() const;

  float getScale(size_t channel = 0) const;
  float getZero(size_t channel = 0) const;
  bool isPerChannel() const;

  size_t getRows() const;
  size_t getCols() const;
};

} // namespace nn::quantization

#endif