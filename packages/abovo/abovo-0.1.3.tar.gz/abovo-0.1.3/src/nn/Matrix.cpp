#include <cstdlib>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>

#include "nn/Matrix.hpp"
#include "nn/matmul/Blocked.hpp"
#include "nn/matmul/SIMD.hpp"

namespace nn {

Matrix::Matrix(int r, int c) : rows(r), cols(c) {
  data = new double *[rows];
  for (int i = 0; i < rows; ++i) {
    data[i] = new double[cols];
  }
}

Matrix::Matrix(int r, int c, double num) : rows(r), cols(c) {
  data = new double *[rows];
  for (int i = 0; i < rows; ++i) {
    data[i] = new double[cols];
    for (int j = 0; j < cols; ++j) {
      data[i][j] = num;
    }
  }
}

Matrix::Matrix() : rows(0), cols(0), data(nullptr) {}

Matrix::Matrix(const std::vector<std::vector<double>> &vec)
    : rows(vec.size()), cols(vec.size() > 0 ? vec[0].size() : 0) {
  data = new double *[rows];
  for (int i = 0; i < rows; ++i) {
    data[i] = new double[cols];
    for (int j = 0; j < cols; ++j) {
      data[i][j] = vec[i][j];
    }
  }
}

Matrix::~Matrix() {
  for (int i = 0; i < rows; ++i) {
    delete[] data[i];
  }
  delete[] data;
}

Matrix::Matrix(const Matrix &other) : rows(other.rows), cols(other.cols) {
  data = new double *[rows];
  for (int i = 0; i < rows; ++i) {
    data[i] = new double[cols];
    for (int j = 0; j < cols; ++j) {
      data[i][j] = other.data[i][j];
    }
  }
}

void Matrix::randomize(double fan_in) {
  std::random_device rd;
  std::mt19937 gen(rd());
  std::normal_distribution<> dist(
      0.0, std::sqrt(2.0 / fan_in)); // He weight initialization

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      data[i][j] = dist(gen);
    }
  }
}

void Matrix::print() const {
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      std::cout << data[i][j] << " ";
    }
    std::cout << std::endl;
  }
}

int Matrix::getRows() const { return rows; }

int Matrix::getCols() const { return cols; }

// pass by reference so no need to copy
Matrix Matrix::operator+(const Matrix &other) const {
  if (rows != other.rows && other.rows != 1) {
    throw std::invalid_argument(
        "Matrix dimensions must match or be broadcasted; got row dimensions: " +
        std::to_string(rows) + " and " + std::to_string(other.rows) + ".");
  }

  if (cols != other.cols) {
    throw std::invalid_argument(
        "Column dimensions must match; got dimensions: " +
        std::to_string(cols) + " and " + std::to_string(other.cols) + ".");
  }

  Matrix res(rows, cols);
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      res.data[i][j] = data[i][j] + other.data[other.rows == 1 ? 0 : i][j];
    }
  }

  return res;
}

Matrix Matrix::operator*(const Matrix &other) const {
  return matmul::multiply_blocked(*this, other);
}

Matrix Matrix::operator*(double scalar) const {
  Matrix res(rows, cols);

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      res.data[i][j] = data[i][j] * scalar;
    }
  }

  return res;
}

Matrix &Matrix::operator=(const Matrix &other) {
  if (this == &other) {
    return *this;
  }

  if (rows != other.rows || cols != other.cols) {
    // Deallocate current memory
    for (int i = 0; i < rows; ++i) {
      delete[] data[i];
    }
    delete[] data;

    // Allocate new memory
    rows = other.rows;
    cols = other.cols;
    data = new double *[rows];
    for (int i = 0; i < rows; ++i) {
      data[i] = new double[cols];
    }
  }

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      data[i][j] = other.data[i][j];
    }
  }

  return *this;
}

double &Matrix::operator()(int row, int col) { return data[row][col]; }

const double &Matrix::operator()(int row, int col) const {
  return data[row][col];
}

Matrix Matrix::transpose() const {
  Matrix result(cols, rows);

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      result.data[j][i] = data[i][j];
    }
  }

  return result;
}

Matrix Matrix::hadamard_product(const Matrix &other) const {
  if (rows != other.rows || cols != other.cols) {
    throw std::invalid_argument(
        "Matrix dimensions must match for hadamard multiplication.");
  }

  Matrix res(rows, cols);

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      res.data[i][j] = this->data[i][j] * other.data[i][j];
    }
  }

  return res;
}

Matrix::MinMaxPair Matrix::getMinMax(double arr[], int low, int high) const {
  MinMaxPair minmax;

  if (low == high) {
    minmax.min = arr[low];
    minmax.max = arr[low];
    return minmax;
  }

  if (high == low + 1) {
    if (arr[low] > arr[high]) {
      minmax.max = arr[low];
      minmax.min = arr[high];
    } else {
      minmax.max = arr[high];
      minmax.min = arr[low];
    }
    return minmax;
  }

  int mid = (low + high) / 2;
  MinMaxPair left = getMinMax(arr, low, mid);
  MinMaxPair right = getMinMax(arr, mid + 1, high);

  minmax.min = std::min(left.min, right.min);
  minmax.max = std::max(left.max, right.max);

  return minmax;
}

Matrix::MinMaxPair Matrix::minmax() const {
  int total = rows * cols;
  double *flat = new double[total];

  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      flat[i * cols + j] = data[i][j];
    }
  }

  MinMaxPair result = getMinMax(flat, 0, total - 1);
  delete[] flat;
  return result;
}

double Matrix::getMin() const { return minmax().min; }

double Matrix::getMax() const { return minmax().max; }

} // namespace nn