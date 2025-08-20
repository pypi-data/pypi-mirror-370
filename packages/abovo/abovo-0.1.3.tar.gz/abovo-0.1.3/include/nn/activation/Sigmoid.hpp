#ifndef NN_ACTIVATION_SIGMOID_HPP
#define NN_ACTIVATION_SIGMOID_HPP

#include "../Activation.hpp"

namespace nn::activation {

Matrix sigmoid(const Matrix &X);
Matrix sigmoid_derivative(const Matrix &X);

} // namespace nn::activation

#endif