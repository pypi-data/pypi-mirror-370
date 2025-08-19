# Lambda Happy
A high‑performance solver for estimating the lambda_happy factor in sparse linear models (≈99% sparsity) using C++/CUDA and PyTorch.

---

## Installation

```bash
# Core functionality
pip install lambda-happy

# Benchmark GUI (PyQt5)
pip install lambda-happy[benchmark]

# Validation tools (PyQt5 + pandas)
pip install lambda-happy[validation]

# All extras (Benchmark + Validation tools)
pip install lambda-happy[all]
```

Then install torch (see: https://pytorch.org/get-started/locally/)
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## What is lambda happy ?
In sparse regression, lambda_happy balances data fidelity against model sparsity.

Given:

- X ∈ R -> The feature matrix
- Z ∈ R -> A random Gaussian projection matrix
- Z_centrer -> centered Z matrix


Lambda_happy is estimated as the 95th percentile of
(norm of the transpose of X times the centered Z matrix, measured in Chebyshev norm) divided by (norm of the centered Z matrix measured in 2-norm), that is:

- lambda_happy = Quantile_0.95 ( || X^T * Z_centrer ||_infinity / || Z_centrer ||_2 )

which requires:
- p: The number of feature in The feature matrix X  (affects only the matmul)
- n: The number of row in The feature matrix x 
- m: number of projections (larger m ⇒ higher precision, but each step’s cost scales with m)

## Quickstart

```py
import torch
from lambda_happy import LambdaHappy

# Prepare data
X = torch.randn(1000, 5000, device="cuda")
# Initialize solver (auto‐select fastest backend)
solver = LambdaHappy(X, force_fastest=True)

# Single estimate
λ = solver.compute(m=5000)
print(f"λ ≈ {λ:.4f}")

# Multiple runs
λs = solver.compute_many(m=5000, nb_run=50)

# Aggregated (mean)
λ_mean = solver.compute_agg(m=5000, nb_run=50, func=torch.mean)
```

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

## Recommended Settings

| Context | Data Type | Notes |
|-|-|-|
| CPU         | `float32`     | Stable, widely supported, and generally the fastest on CPU.          |
| CUDA GPU    | `float16`     | High performance if `X` is normalized; otherwise use `float32`.      |
| Backend     | `"AUTOMATIC"` | Selects the best available implementation based on hardware and dtype. |

## Extras

### Benchmark

The `lambda-happy-benchmark` script measures and compares the performance of LambdaHappy on CPU and GPU.
It offers various benchmarking options and displays live throughput plots.
Example usage:
```sh
lambda-happy-benchmark --benchmark_2D --benchmark_3D --device cuda --dtype float16 -n 1000 -p 1000 -m 10000
```
This runs a 2D benchmark using CUDA with specified matrix dimensions and then run a 3D benchmark.
> ℹ️ Note: Not all hyperparameters are used for every plot, but if provided, they will be applied when relevant.

### Validation

The `lambda-happy-validation` script runs tests to validate lambda_happy estimation accuracy.
It generates detailed reports and distribution plots using pandas and PyQt5.

Example usage:
```sh
lambda-happy-validation --distribution_small --device cuda --dtype float32 -n 1000 -p 1000
```
This plots small-scale lambda_happy distributions on cuda for the given parameters.

### Results
Here are the results for a CUDA calculation :
| Rang | Mode     | Version       | Précision | FPS    | Speed-up |
|-------|----------|---------------|-----------|--------|----------|
| 1     | Mono-GPU | SMART_TENSOR  | Float32   | 449    | 1.00x    |
| 2     | Mono-GPU | GPU_DEDICATED | Float32   | 501    | 1.12x    |
| 3     | Multi-GPU| SMART_TENSOR  | Float32   | 511    | 1.14x    |
| 4     | Multi-GPU| SMART_TENSOR  | Float16   | 664    | 1.48x    |
| 5     | Multi-GPU| GPU_DEDICATED | Float32   | 911    | 2.03x    |
| 6     | Mono-GPU | SMART_TENSOR  | Float16   | 1'215  | 2.71x    |
| 7     | Mono-GPU | GPU_DEDICATED | Float16   | 1'618  | 3.60x    |
| 8     | Multi-GPU| GPU_DEDICATED | Float16   | 2'104  | 4.69x    |

The test server is equipped with an Intel Xeon E5-2699 v3 processor and three NVIDIA GeForce RTX 2080 Ti graphics cards.

It uses the default parameters for the evaluation with X of size 1000x1000 and m=10000.
> ℹ️ Note: Use device="cuda" when you create X.

# About This Project
This package is developed as part of the Bachelor’s thesis by Yerly Sevan at HE-Arc, supervised by Cédric Billat.

For questions or contact: sevan.yerly@he-arc.ch