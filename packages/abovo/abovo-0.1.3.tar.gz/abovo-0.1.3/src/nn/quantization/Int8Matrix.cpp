#include "nn/quantization/Int8Matrix.hpp"
#include <algorithm>
#include <cmath>
#include <limits>

namespace nn::quantization {

Int8Matrix::Int8Matrix(size_t rows, size_t cols)
    : rows(rows), cols(cols), data(rows * cols, 0), scales(1, 1.0f),
      zeros(1, 0.0f), per_channel(false) {}

Int8Matrix::Int8Matrix(size_t rows, size_t cols, float scale, float zero)
    : rows(rows), cols(cols), data(rows * cols, 0), scales(1, scale),
      zeros(1, zero), per_channel(false) {}

int8_t &Int8Matrix::operator()(size_t i, size_t j) {
  return data[i * cols + j];
}

const int8_t &Int8Matrix::operator()(size_t i, size_t j) const {
  return data[i * cols + j];
}

Int8Matrix Int8Matrix::quantize_per_tensor(const nn::Matrix &X) {
  size_t rows = X.getRows();
  size_t cols = X.getCols();

  double min_val = X.getMin();
  double max_val = X.getMax();

  // symmetric quantization
  float abs_max = std::max(std::fabs(min_val), std::fabs(max_val));
  float scale = abs_max / 127.0f;
  float zero = 0.0f;

  Int8Matrix res(rows, cols, scale, zero);

  for (size_t i = 0; i < rows; ++i) {
    for (size_t j = 0; j < cols; ++j) {
      float value = X(i, j);
      int32_t quantized = std::round(value / scale);
      // Clamp to [-127, 127] range
      quantized = std::max(-127, std::min(127, quantized));
      res(i, j) = static_cast<int8_t>(quantized);
    }
  }

  return res;
}

Int8Matrix Int8Matrix::quantize_per_channel(const nn::Matrix &X) {
  size_t rows = X.getRows();
  size_t cols = X.getCols();

  Int8Matrix res(rows, cols);
  res.per_channel = true;
  res.scales.resize(cols);
  res.zeros.resize(cols);

  for (size_t j = 0; j < cols; ++j) {
    double min_val = std::numeric_limits<double>::max();
    double max_val = std::numeric_limits<double>::lowest();

    for (size_t i = 0; i < rows; ++i) {
      min_val = std::min(min_val, X(i, j));
      max_val = std::max(max_val, X(i, j));
    }

    float abs_max = std::max(std::fabs(min_val), std::fabs(max_val));
    res.scales[j] = abs_max / 127.0f;
    res.zeros[j] = 0.0f;

    for (size_t i = 0; i < rows; ++i) {
      float value = X(i, j);
      int32_t quantized = std::round(value / res.scales[j]);
      quantized = std::max(-127, std::min(127, quantized));
      res(i, j) = static_cast<int8_t>(quantized);
    }
  }

  return res;
}

nn::Matrix Int8Matrix::dequantize() const {
  nn::Matrix res(rows, cols);

  if (per_channel) {
    for (size_t j = 0; j < cols; ++j) {
      float scale = scales[j];
      float zero = zeros[j];

      for (size_t i = 0; i < rows; ++i) {
        res(i, j) = (operator()(i, j) * scale) + zero;
      }
    }
  } else {
    float scale = scales[0];
    float zero = zeros[0];

    for (size_t i = 0; i < rows; ++i) {
      for (size_t j = 0; j < cols; ++j) {
        res(i, j) = (operator()(i, j) * scale) + zero;
      }
    }
  }

  return res;
}

float Int8Matrix::getScale(size_t channel) const {
  if (per_channel && channel < scales.size()) {
    return scales[channel];
  }
  return scales[0];
}

float Int8Matrix::getZero(size_t channel) const {
  if (per_channel && channel < zeros.size()) {
    return zeros[channel];
  }
  return zeros[0];
}

bool Int8Matrix::isPerChannel() const { return per_channel; }

size_t Int8Matrix::getRows() const { return rows; }

size_t Int8Matrix::getCols() const { return cols; }

} // namespace nn::quantization