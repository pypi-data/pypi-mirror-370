#ifndef NN_ACTIVATION_SOFTMAX_HPP
#define NN_ACTIVATION_SOFTMAX_HPP

#include "../Activation.hpp"

namespace nn::activation {

Matrix softmax(const Matrix &X);
Matrix softmax_derivative(const Matrix &X);

} // namespace nn::activation

#endif