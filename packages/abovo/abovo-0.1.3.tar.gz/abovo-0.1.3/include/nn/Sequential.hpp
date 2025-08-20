#ifndef NN_SEQUENTIAL_HPP
#define NN_SEQUENTIAL_HPP
#include <vector>

#include "DenseLayer.hpp"
#include "Loss.hpp"

namespace nn {

class Sequential {
private:
  std::vector<DenseLayer> layers;
  Loss loss;
  bool qat;

  int optimizer_iteration;
  bool use_adam;
  double beta1;
  double beta2;
  double epsilon;

public:
  Sequential();

  void add(const DenseLayer &layer);
  Matrix forward(const Matrix &X);
  void print() const;

  void backward(const Matrix &y_pred, const Matrix &y_true,
                double learning_rate, LossType loss_type = LossType::MSE);

  void train(const Matrix &X, const Matrix &y, int epochs, int batch_size,
             double learning_rate, LossType loss_type);

  double evaluate(const Matrix &X_test, const Matrix &y_test);

  void quantizeAll(bool per_channel = true);
  void dequantizeAll();
  bool isQuantized() const;

  void enableQAT(bool enable);

  void enableAdam(bool enable = true, double b1 = 0.9, double b2 = 0.999,
                  double eps = 1e-8);
};

} // namespace nn

#endif