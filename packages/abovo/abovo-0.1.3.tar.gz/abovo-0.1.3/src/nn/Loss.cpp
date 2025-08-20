#include <cstdlib>
#include <iostream>
#include <stdexcept>

#include "nn/Loss.hpp"
#include "nn/loss/CrossEntropy.hpp"
#include "nn/loss/MSE.hpp"

namespace nn {

double Loss::loss(const Matrix &y_pred, const Matrix &y_true,
                  LossType type) const {
  switch (type) {
  case LossType::CROSS_ENTROPY:
    return loss::cross_entropy(y_pred, y_true);
  default:
    return loss::mse(y_pred, y_true);
  }
}

Matrix Loss::loss_derivative(const Matrix &y_pred, const Matrix &y_true,
                             LossType type) const {
  switch (type) {
  case LossType::CROSS_ENTROPY:
    return loss::cross_entropy_derivative(y_pred, y_true);
  default:
    return loss::mse_derivative(y_pred, y_true);
  }
}

} // namespace nn