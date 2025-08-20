#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>

#include "nn/Sequential.hpp"

namespace nn {

Sequential::Sequential()
    : qat(false), optimizer_iteration(0), use_adam(false), beta1(0.9),
      beta2(0.999), epsilon(1e-8) {}

void Sequential::enableAdam(bool enable, double b1, double b2, double eps) {
  this->use_adam = enable;
  this->beta1 = b1;
  this->beta2 = b2;
  this->epsilon = eps;
  this->optimizer_iteration = 0;
}

Matrix Sequential::forward(const Matrix &X) {
  Matrix out = X;

  for (auto &layer : layers) {
    out = layer.forward(out);
    out = layer.activation(out);
  }

  return out;
}

void Sequential::backward(const Matrix &y_pred, const Matrix &y_true,
                          double learning_rate, LossType loss_type) {
  Matrix gradient = loss.loss_derivative(y_pred, y_true, loss_type);

  if (this->use_adam) {
    this->optimizer_iteration++;
    for (int i = layers.size() - 1; i >= 0; --i) {
      gradient = layers[i].backwardAdam(gradient, learning_rate, this->beta1,
                                        this->beta2, this->epsilon,
                                        this->optimizer_iteration);
    }
  } else {
    for (int i = layers.size() - 1; i >= 0; --i) {
      gradient = layers[i].backward(gradient, learning_rate);
    }
  }
}

void Sequential::add(const DenseLayer &layer) { layers.push_back(layer); }

void Sequential::print() const {
  for (auto &layer : layers) {
    layer.print();
  }
}

void Sequential::enableQAT(bool enable) { this->qat = enable; }

// mini-batch implementation
void Sequential::train(const Matrix &X, const Matrix &y, int epochs,
                       int batch_size, double learning_rate,
                       LossType loss_type) {
  int num_samples = X.getRows();
  int X_cols = X.getCols();
  int y_cols = y.getCols();

  std::vector<int> indices(num_samples);
  for (int i = 0; i < num_samples; ++i) {
    indices[i] = i;
  }

  std::random_device rd;
  std::mt19937 g(rd());

  for (int epoch = 0; epoch < epochs; ++epoch) {
    std::shuffle(indices.begin(), indices.end(), g);

    double epoch_loss = 0.0;
    int num_batches = ceil(static_cast<double>(num_samples) / batch_size);

    for (int batch = 0; batch < num_batches; ++batch) {
      int start_idx = batch * batch_size;
      int end_idx = std::min((batch + 1) * batch_size, num_samples);
      int current_batch_size = end_idx - start_idx;

      Matrix batch_X(current_batch_size, X_cols);
      Matrix batch_y(current_batch_size, y_cols);

      for (int i = 0; i < current_batch_size; ++i) {
        int idx = indices[start_idx + i];

        for (int j = 0; j < X_cols; ++j) {
          batch_X(i, j) = X(idx, j);
        }
        for (int j = 0; j < y_cols; ++j) {
          batch_y(i, j) = y(idx, j);
        }
      }

      // if QAT enabled, apply to forward pass
      if (qat) {
        for (auto &layer : layers) {
          layer.simulateQuantization();
        }
      }

      Matrix preds = forward(batch_X);

      double batch_loss = loss.loss(preds, batch_y, loss_type);
      epoch_loss += batch_loss;

      backward(preds, batch_y, learning_rate, loss_type);
    }

    epoch_loss /= num_batches;

    if (epoch % 10 == 0 || epoch == epochs - 1) {
      std::cout << "Epoch " << epoch + 1 << "/" << epochs
                << " - Loss: " << epoch_loss << std::endl;

      if (epoch % 10 == 0 && epoch > 0) {
        int eval_size = std::min(1000, static_cast<int>(X.getRows()));
        Matrix X_subset(eval_size, X.getCols());
        Matrix y_subset(eval_size, y.getCols());

        for (int i = 0; i < eval_size; ++i) {
          for (int j = 0; j < X.getCols(); ++j) {
            X_subset(i, j) = X(i, j);
          }
          for (int j = 0; j < y.getCols(); ++j) {
            y_subset(i, j) = y(i, j);
          }
        }

        double accuracy = evaluate(X_subset, y_subset);
        std::cout << "- Current training accuracy: " << accuracy * 100 << "%"
                  << std::endl;
      }
    }
  }
}

// finds max value = prediction and label
double Sequential::evaluate(const Matrix &X_test, const Matrix &y_test) {
  Matrix y_pred = forward(X_test);
  int correct = 0;

  for (int i = 0; i < y_pred.getRows(); ++i) {
    int pred_label = 0;
    double max_pred = y_pred(i, 0);
    for (int j = 1; j < y_pred.getCols(); ++j) {
      if (y_pred(i, j) > max_pred) {
        max_pred = y_pred(i, j);
        pred_label = j;
      }
    }

    int true_label = 0;
    double max_true = y_test(i, 0);
    for (int j = 1; j < y_test.getCols(); ++j) {
      if (y_test(i, j) > max_true) {
        max_true = y_test(i, j);
        true_label = j;
      }
    }

    if (pred_label == true_label)
      ++correct;
  }

  return static_cast<double>(correct) / X_test.getRows();
}

void Sequential::quantizeAll(bool per_channel) {
  for (auto &layer : layers) {
    layer.quantize(per_channel);
  }
}

void Sequential::dequantizeAll() {
  for (auto &layer : layers) {
    layer.dequantize();
  }
}

bool Sequential::isQuantized() const {
  for (const auto &layer : layers) {
    if (!layer.isQuantized()) {
      return false;
    }
  }
  return true;
}

} // namespace nn