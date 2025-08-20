#ifndef NN_ACTIVATION_RELU_HPP
#define NN_ACTIVATION_RELU_HPP

#include "../Activation.hpp"

namespace nn::activation {

Matrix relu(const Matrix &X);
Matrix relu_derivative(const Matrix &X);

} // namespace nn::activation

#endif