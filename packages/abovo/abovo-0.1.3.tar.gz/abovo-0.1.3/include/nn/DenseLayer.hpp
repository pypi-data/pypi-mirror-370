#ifndef NN_DENSELAYER_HPP
#define NN_DENSELAYER_HPP

#include "Activation.hpp"
#include "Matrix.hpp"
#include "nn/quantization/Int8Matrix.hpp"

namespace nn {

class DenseLayer {
private:
  int input_size;
  int output_size;
  Matrix weights;
  Matrix biases;

  Matrix last_input;
  // where z = w * x + b
  Matrix last_linear_output;

  ActivationType activation_type;

  bool is_quantized;
  quantization::Int8Matrix quantized_weights;
  quantization::Int8Matrix quantized_biases;

  Matrix m_weights; // first moment (momentum)
  Matrix m_biases;
  Matrix v_weights; // second moment (velocity)
  Matrix v_biases;
  bool optimizer_initialized = false;

public:
  DenseLayer(int in, int out, ActivationType activation_type);

  Matrix forward(const Matrix &X);
  Matrix activation(const Matrix &X) const;
  void print() const;

  Matrix backward(const Matrix &d_out, double eta);

  void quantize(bool per_channel = true);
  void dequantize();
  bool isQuantized() const;

  void simulateQuantization(); // Quantization-Aware Training

  void initializeOptimizer();
  Matrix backwardAdam(const Matrix &incoming_gradient, double learning_rate,
                      double beta1, double beta2, double epsilon, int t);
};

} // namespace nn

#endif