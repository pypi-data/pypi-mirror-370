#ifndef NN_MATRIX_HPP
#define NN_MATRIX_HPP

#include <utility>
#include <vector>

namespace nn {

class Matrix {
private:
  int rows, cols;
  double **data;

  struct MinMaxPair {
    double min;
    double max;
  };

  // helper tournament method
  MinMaxPair getMinMax(double arr[], int low, int high) const;
  MinMaxPair minmax() const;

public:
  Matrix(int r, int c);
  Matrix(int r, int c, double val);
  Matrix();
  ~Matrix();
  Matrix(const std::vector<std::vector<double>> &vec);
  Matrix(const Matrix &other);

  void randomize(double fan_in);
  void print() const;
  int getRows() const;
  int getCols() const;

  // won't change any member data within the function
  Matrix operator+(const Matrix &other) const;
  Matrix operator*(const Matrix &other) const;
  Matrix operator*(double scalar) const;
  Matrix &operator=(const Matrix &other);
  // modifiable
  double &operator()(int row, int col);
  // getter
  const double &operator()(int row, int col) const;

  Matrix transpose() const;
  Matrix hadamard_product(const Matrix &other) const;

  double getMin() const;
  double getMax() const;
};

} // namespace nn

#endif