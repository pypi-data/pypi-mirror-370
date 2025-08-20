<p align="center">
  <img src="https://raw.githubusercontent.com/emirdur/NN-ab-ovo/main/assets/abovo_logo.svg" width="300" alt="abovo logo"/>
</p>

---

[![docs](https://readthedocs.org/projects/nn-ab-ovo/badge/?version=latest)](https://nn-ab-ovo.readthedocs.io/en/latest/?badge=latest)
[![tests](https://github.com/emirdur/NN-ab-ovo/actions/workflows/tests.yml/badge.svg)](https://github.com/emirdur/NN-ab-ovo/actions)
[![pypi](https://badge.fury.io/py/abovo.svg)](https://pypi.org/project/abovo/)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/emirdur/NN-ab-ovo/badge)](https://scorecard.dev/viewer/?uri=github.com/emirdur/NN-ab-ovo)
[![downloads](https://static.pepy.tech/badge/abovo)](https://pepy.tech/projects/abovo)

NN-ab-ovo (abovo) is a neural network engine written in C++ with Python bindings, designed to teach systems-level ML optimizations like threading, cache efficiency, hardware acceleration, and quantization.

---

## Features

- C++ backend with modular layers and training pipeline
- Python API via `pybind11` bindings (`pip install abovo`)
- Optimizations: SIMD, OpenMP multithreading, cache blocking
- Post-training quantization (PTQ) and quantization-aware training (QAT) (FP32 → INT8)
- Profiling support (Valgrind, cache misses, instruction counts)

## Installation

```bash
pip install abovo
```

> Requires a C++17-compatible compiler and OpenMP support.

## Example (XOR)

```python
from abovo import Sequential, DenseLayer, Matrix, ActivationType, LossType

X = Matrix(4, 2)
X[0, 0] = 0; X[0, 1] = 0
X[1, 0] = 0; X[1, 1] = 1
X[2, 0] = 1; X[2, 1] = 0
X[3, 0] = 1; X[3, 1] = 1

y = Matrix(4, 1)
y[0, 0] = 0
y[1, 0] = 1
y[2, 0] = 1
y[3, 0] = 0

model = Sequential()
model.add(DenseLayer(2, 4, ActivationType.RELU))
model.add(DenseLayer(4, 1, ActivationType.SIGMOID))
model.train(X, y, epochs=100, batch_size=1, learning_rate=0.1, loss_type=LossType.MSE)
```

## Build (C++ Only)

You can either build natively or in Docker. Note the provided Dockerfile runs valgrind, so adjust as needed to run the correct binary. Recommended on Apple Silicon for x86 builds.

**Native Build (Mac/Linux):**

```bash
make
./NN-ab-ovo
```

**Docker (x86_64 emulation):**

```bash
docker build -t nn-ab-ovo .
docker run --rm nn-ab-ovo
```

> Make sure the MNIST dataset files (`train-images.idx3-ubyte`, `train-labels.idx1-ubyte`, etc.) are in the project root or mounted into the Docker container.

## Datasets

- **XOR**: Validates non-linear separability
- **MNIST**: Handwritten digit classification

## Optimizations

Optimization experiments are documented in the GitHub repository under [optimizations.md](https://github.com/emirdur/NN-ab-ovo/blob/main/tests/optimizations/optimizations.md), including:

- Naive vs. blocked matrix multiplication
- Compiler flag benchmarking
- L1/L2 cache miss analysis (Valgrind)
- OpenMP and SIMD speedups
- Timing analysis with `std::chrono`

These experiments help evaluate system-level performance, guide improvements for training/inference, and validate optimizations available to the community.

## Project Structure

The GitHub repository features the following project structure:

- `Matrix.hpp / Matrix.cpp`: Core matrix operations and linear algebra utilities.
- `DenseLayer.hpp / DenseLayer.cpp`: Fully connected layer with forward and backward pass.
- `Activation.hpp / Activation.cpp`: Support for activation functions (e.g., ReLU, LeakyReLU, Sigmoid).
- `Loss.hpp`: Interface for loss functions (e.g., MSE, CrossEntropy).
- `Sequential.hpp / Sequential.cpp`: High-level container for layer sequencing and model training.
- `tests`: Directory containing runnable code on specific datasets.

The engine is modular: activation functions, loss functions, and layers are easily swappable for flexibility and experimentation.

## Documentation

Read the full docs at: [https://nn-ab-ovo.readthedocs.io/](https://nn-ab-ovo.readthedocs.io/).

## Why “ab ovo”?

_"From the egg" — the library was built from the ground up, with performance and pedagogy in mind._

## Future Work

- [ ] Switch Design Pattern for Activation + Loss
- [ ] Switch Matrix class to use size_t + Refactor
- [ ] More comprehensive Softmax implementation
- [ ] Continue with optimizations
- [ ] Add support for convolutional layers
- [ ] Implement GPU acceleration (Metal or CUDA)
- [ ] LLVMs?

## Disclaimer

NN-ab-ovo (abovo) is an independent open-source project and is not affiliated with or endorsed by any company or organization.

## License

MIT License
