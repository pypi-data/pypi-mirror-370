#include "nn/Activation.hpp"
#include "nn/DenseLayer.hpp"
#include "nn/Loss.hpp"
#include "nn/MatMul.hpp"
#include "nn/Matrix.hpp"
#include "nn/Sequential.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace nn;

PYBIND11_MODULE(_abovo, m) {
  py::enum_<MatMulType>(m, "MatMulType")
      .value("NAIVE", MatMulType::NAIVE)
      .value("BLOCKED", MatMulType::BLOCKED)
      .value("SIMD", MatMulType::SIMD)
      .value("SIMD_MT", MatMulType::SIMD_MT)
      // .value("METAL_GPU", MatMulType::METAL_GPU)
      .export_values();

  py::enum_<LossType>(m, "LossType")
      .value("MSE", LossType::MSE)
      .value("CrossEntropy", LossType::CROSS_ENTROPY)
      .export_values();

  py::enum_<ActivationType>(m, "ActivationType")
      .value("RELU", ActivationType::RELU)
      .value("LEAKY_RELU", ActivationType::LEAKY_RELU)
      .value("SIGMOID", ActivationType::SIGMOID)
      .value("SOFTMAX", ActivationType::SOFTMAX)
      .export_values();

  py::class_<Matrix>(m, "Matrix")
      .def(py::init<int, int>())
      .def(py::init<const std::vector<std::vector<double>> &>())
      .def("get_rows", &Matrix::getRows)
      .def("get_cols", &Matrix::getCols)
      .def("transpose", &Matrix::transpose)
      .def("get_min", &Matrix::getMin)
      .def("get_max", &Matrix::getMax)
      .def("__getitem__",
           [](const Matrix &m, std::pair<int, int> idx) {
             return m(idx.first, idx.second);
           })
      .def("__setitem__", [](Matrix &m, std::pair<int, int> idx,
                             double val) { m(idx.first, idx.second) = val; })
      .def("print", &Matrix::print);

  py::class_<DenseLayer>(m, "DenseLayer")
      .def(py::init<int, int, ActivationType>())
      .def("forward", &DenseLayer::forward)
      .def("print", &DenseLayer::print)
      .def("quantize", &DenseLayer::quantize)
      .def("dequantize", &DenseLayer::dequantize)
      .def("is_quantized", &DenseLayer::isQuantized);

  py::class_<Sequential>(m, "Sequential")
      .def(py::init<>())
      .def("add", &Sequential::add)
      .def("forward", &Sequential::forward)
      .def("train", &Sequential::train, py::arg("X"), py::arg("y"),
           py::arg("epochs"), py::arg("batch_size"), py::arg("learning_rate"),
           py::arg("loss_type") = LossType::MSE)
      .def("evaluate", &Sequential::evaluate)
      .def("quantize_all", &Sequential::quantizeAll,
           py::arg("per_channel") = true)
      .def("dequantize_all", &Sequential::dequantizeAll)
      .def("enable_qat", &Sequential::enableQAT)
      .def("enable_adam", &Sequential::enableAdam, py::arg("enable") = true,
           py::arg("beta1") = 0.9, py::arg("beta2") = 0.999,
           py::arg("epsilon") = 1e-8)
      .def("print", &Sequential::print);
}