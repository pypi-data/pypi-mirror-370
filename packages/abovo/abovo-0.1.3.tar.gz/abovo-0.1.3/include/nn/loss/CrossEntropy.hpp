#ifndef NN_LOSS_CROSS_ENTROPY_HPP
#define NN_LOSS_CROSS_ENTROPY_HPP

#include "../Loss.hpp"

namespace nn::loss {

double cross_entropy(const Matrix &y_pred, const Matrix &y_true);
Matrix cross_entropy_derivative(const Matrix &y_pred, const Matrix &y_true);

} // namespace nn::loss

#endif