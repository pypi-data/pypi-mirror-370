#ifndef NN_MSE_HPP
#define NN_MSE_HPP

#include "../Loss.hpp"

namespace nn::loss {

double mse(const Matrix &y_pred, const Matrix &y_true);
Matrix mse_derivative(const Matrix &y_pred, const Matrix &y_true);

} // namespace nn::loss

#endif
