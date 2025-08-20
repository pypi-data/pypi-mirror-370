#ifndef NN_ACTIVATION_LEAKY_RELU_HPP
#define NN_ACTIVATION_LEAKY_RELU_HPP

#include "../Activation.hpp"

namespace nn::activation {

Matrix leaky_relu(const Matrix &X, double alpha = 0.01);
Matrix leaky_relu_derivative(const Matrix &X, double alpha = 0.01);

} // namespace nn::activation

#endif