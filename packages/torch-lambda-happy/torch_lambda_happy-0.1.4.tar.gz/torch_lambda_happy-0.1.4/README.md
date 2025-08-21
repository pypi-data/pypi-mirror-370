# Lambda Happy

# Abstract

In Data Science, the goal is often to explain the target variable **Y** in terms of the input **X** as:

![formula](<https://latex.codecogs.com/svg.latex?Y=f_\alpha(X)+\varepsilon>)

where

- ![eps](<https://latex.codecogs.com/svg.latex?\varepsilon\sim\mathcal{N}(0,1)>) is Gaussian noise,

- **X** is an _n × p_ data matrix,

- **Y** is an _n × 1_ vector,

- and **α** represents the model parameters.

The function _f_ can be linear or nonlinear, for instance implemented as a neural network.

In this case, **α** corresponds to the set of weights and biases of the network.

Sylvain Sardy (ref) proposed a relaxation technique to estimate the parameters **α**:

![alpha_hat](<https://latex.codecogs.com/svg.latex?\hat{\alpha}=\arg\min_{\alpha};|Y-f_\alpha(X)|_2+\lambda|\alpha|_1>)

One of the main challenges is choosing the regularization parameter **λ**.

- If **λ** is too small, the resulting model will be overly sparse and inaccurate.

- If **λ** is too large, the model will be accurate but not sparse enough.

The goal is to find the best trade-off.

The package implements Sardy’s algorithm to compute the optimal **λ**.

The implementation automatically runs on one or multiple GPUs if available, or on the CPU otherwise.

An auto-detection feature ensures the best use of the available hardware.

The optimal value, referred to as the **“happy lambda”**, is computed as:

![lambda_happy](<https://latex.codecogs.com/svg.latex?\lambda_{\text{happy}}=\text{Quantile}_{0.95}\left(\frac{|X^\top%20Z_{\text{centered}}|_\infty}{|Z_{\text{centered}}|_2}\right)>)

where the numerator uses the Chebyshev (L∞) norm and the denominator the Euclidean (L2) norm.

Here, ![Z](https://latex.codecogs.com/svg.latex?Z_{\text{centered}}) is an _n × m_ random matrix (with _m_ typically large enough for accurate quantile estimation).

Each column of **Z** is drawn independently from ![N](<https://latex.codecogs.com/svg.latex?\mathcal{N}(0,1)>) and then centered (its mean is subtracted so that every column has zero mean).

A high-performance CPU/GPU solver for estimating the lambda_happy factor in sparse linear models (≈99% sparsity) using PyTorch, compatible with Windows, Linux, and macOS.

## Installation

```bash
# Core functionality
pip install torch-lambda-happy

# Benchmark GUI (PyQt5)
pip install torch-lambda-happy[benchmark]

# Validation tools (PyQt5 + pandas)
pip install torch-lambda-happy[validation]

# All extras (Benchmark + Validation tools)
pip install torch-lambda-happy[all]
```

Then install torch (see: https://pytorch.org/get-started/locally/)

Here is the current command in August 2025 for Linux :

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Quickstart

### Recommended use case

```py
import torch
from torch_lambda_happy import LambdaHappy

# Prepare data
X = torch.randn(1000, 5000, device="cuda")

# Initialize solver (auto‐select fastest backend)
solver = LambdaHappy(X, force_fastest=True)

# Single estimate
lambda_value = solver.compute(m=10000)
print(f"lambda_value ≈ {lambda_value:.4f}")

# Multiple runs
lambda_values = solver.compute_many(m=10000, nb_run=50)
print(f"lambda_values ≈ {lambda_values}")

# Aggregated (mean)
lambda_mean = solver.compute_agg(m=10000, nb_run=500, func=torch.median)
print(f"lambda_mean ≈ {lambda_mean:.4f}")
```

### Example with all parameters (single estimation)

```py
import torch
from torch_lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=False, use_multigpu=False)
lambda_ = model.compute(m=10_000, dtype=torch.float16, device_type="cuda")
print(f"Estimated λ: {lambda_:.4f}")

```

### Example with all parameters (many estimations)

```py
import torch
from torch_lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=False)
lambda_ = model.compute_many(m=10_000, dtype=torch.float32, device_type="cuda", nb_run=100)
print(f"Estimated λs: {lambda_}")
```

### Example with all parameters (aggregated estimation)

```py

import torch
from torch_lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=True)
lambda_ = model.compute_agg(
    m=10_000, dtype=torch.float32, device_type="cpu", nb_run=10, func=torch.median
)
print(f"Estimated λ: {lambda_:.4f}")

```

> ⚠️ The examples above illustrate different ways of using the library, but they are not necessarily the fastest methods.  
> For the most efficient versions, please refer to the **Recommended use case** section.

> ℹ️ Use `float16` (or `force_fastest=True`) on **GPU** only if the input matrix **X** is normalized.
> Setting `use_multigpu=True` will utilize all available GPUs if more than one is present.

## What is lambda happy ?

In a sparse model, lambda_happy balances data fidelity against model sparsity.

Given:

- X ∈ R -> The feature matrix
- Z ∈ R -> A random Gaussian projection matrix
- Z_centrer -> centered Z matrix

Lambda_happy is estimated as the 95th percentile of
(norm of the transpose of X times the centered Z matrix, measured in Chebyshev norm) divided by (norm of the centered Z matrix measured in 2-norm), that is:

- lambda_happy = Quantile_0.95 ( || X^T \* Z_centrer ||\_infinity / || Z_centrer ||\_2 )

which requires:

- p: The number of features in the matrix X (affects only the matmul)
- n: The number of rows in the matrix X
- m: The number of projections (larger m ⇒ higher precision, but each step’s cost scales with m)

## Performance Trade-Offs

### Projection Dimension (m)

- ↑ **m** → improves lambda_happy precision.
- ↑ **m** → linearly increases compute time (all kernels scale with m).
- Recommended: **m = 10,000** provides good accuracy in most cases.

> ℹ️ Use `float16` on **GPU** only if the input matrix **X** is normalized.
> Otherwise, lambda_happy estimation may be unstable or inconsistent.

### Sample Dimension (n)

- ↑ **n** → increases cost in all kernels (since Z ∈ R^(n × m)), except for the quantile post-processing step.

### Feature Dimension (p)

- ↑ **p** → only affects the **X^T·Z** matrix multiplication.

---

### Recommended Settings

| Context  | Data Type | Notes                                                           |
| -------- | --------- | --------------------------------------------------------------- |
| CPU      | `float32` | Stable, widely supported, and generally the fastest on CPU.     |
| CUDA GPU | `float16` | High performance if `X` is normalized; otherwise use `float32`. |

# Extras

## Benchmark

The `torch-lambda-happy-benchmark` script measures and compares the performance of LambdaHappy on CPU and GPU.
It offers various benchmarking options and displays live throughput plots.
Example usage:

```sh
torch-lambda-happy-benchmark --benchmark_2D --benchmark_3D --benchmark_float --device cuda --dtype float32 -n 1000 -p 1000 -m 10000
```

This runs a 2D benchmark using CUDA with specified matrix dimensions and then run a 3D benchmark.

> ℹ️ Note: Not all hyperparameters are used for every plot, but if provided, they will be applied when relevant.

## Validation

The `torch-lambda-happy-validation` script runs tests to validate lambda_happy estimation accuracy.
It generates detailed reports and distribution plots using pandas and PyQt5.

Example usage:

```sh
torch-lambda-happy-validation --distribution_small --distribution_large --device cuda --dtype float32 -n 1000 -p 1000
```

This plots small-scale lambda_happy distributions on cuda for the given parameters.

## Results

Here are the results for a CUDA calculation :
| Rang | Mode | Précision | FPS | Speed-up |
|-|-|-|-|-|
| 1 | Mono-GPU | Float32 | 449 | 1.00x |
| 2 | Multi-GPU| Float32 | 511 | 1.14x |
| 3 | Multi-GPU| Float16 | 664 | 1.48x |
| 4 | Mono-GPU | Float16 | 1'215 | 2.71x |

> ℹ️ FPS : number of times the lambda_happy factor is estimated per second.

The test server is equipped with an Intel Xeon E5-2699 v3 processor (2014) and three NVIDIA GeForce RTX 2080 Ti graphics cards (2018).

It uses the default parameters for the evaluation with X of size 1000x1000 and m=10000.

> ℹ️ Note: Use device="cuda" when you create X.

# About This Project

This package, including performance optimizations, was developed as part of a Bachelor’s thesis at HE-Arc by Sevan Yerly (sevan.yerly@he-arc.ch), under the supervision of Cédric Bilat (cedric.bilat@he-arc.ch). The mathematical foundations were developed by Sylvain Sardy (sylvain.sardy@unige.ch).

For questions or contact: sevan.yerly@he-arc.ch or cedric.bilat@he-arc.ch
