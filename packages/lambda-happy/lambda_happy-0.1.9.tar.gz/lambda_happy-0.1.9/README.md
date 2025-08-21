# Lambda Happy

A high-performance CPU/GPU solver for estimating the lambda_happy factor in sparse linear models (≈99% sparsity) using C++/CUDA and PyTorch. Currently compatible only with Python 3.10 on Linux x86_64.

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

Here is the current command in August 2025 for Linux :

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Quickstart

### Recommended use case

```py
import torch
from lambda_happy import LambdaHappy

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
from lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=False, use_multigpu=False)
lambda_ = model.compute(m=10_000, version="AUTOMATIC", dtype=torch.float16, device_type="cuda")
print(f"Estimated λ: {lambda_:.4f}")

```

### Example with all parameters (many estimations)

```py
import torch
from lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=False)
lambda_ = model.compute_many(m=10_000, version="AUTOMATIC", dtype=torch.float32, device_type="cuda", nb_run=100)
print(f"Estimated λs: {lambda_}")
```

### Example with all parameters (aggregated estimation)

```py

import torch
from lambda_happy import LambdaHappy

matX = torch.randn(1_000, 1_000)
model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=True)
lambda_ = model.compute_agg(
    m=10_000, version="AUTOMATIC", dtype=torch.float32, device_type="cpu", nb_run=10, func=torch.median
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

| Context  | Data Type     | Notes                                                                  |
| -------- | ------------- | ---------------------------------------------------------------------- |
| CPU      | `float32`     | Stable, widely supported, and generally the fastest on CPU.            |
| CUDA GPU | `float16`     | High performance if `X` is normalized; otherwise use `float32`.        |
| Backend  | `"AUTOMATIC"` | Selects the best available implementation based on hardware and dtype. |

# Extras

## Benchmark

The `lambda-happy-benchmark` script measures and compares the performance of LambdaHappy on CPU and GPU.
It offers various benchmarking options and displays live throughput plots.
Example usage:

```sh
lambda-happy-benchmark --benchmark_2D --benchmark_3D --benchmark_float --device cuda --dtype float32 -n 1000 -p 1000 -m 10000
```

This runs a 2D benchmark using CUDA with specified matrix dimensions and then run a 3D benchmark.

> ℹ️ Note: Not all hyperparameters are used for every plot, but if provided, they will be applied when relevant.

## Validation

The `lambda-happy-validation` script runs tests to validate lambda_happy estimation accuracy.
It generates detailed reports and distribution plots using pandas and PyQt5.

Example usage:

```sh
lambda-happy-validation --distribution_small --distribution_large --device cuda --dtype float32 -n 1000 -p 1000
```

This plots small-scale lambda_happy distributions on cuda for the given parameters.

## Results

Here are the results for a CUDA calculation :
| Rang | Mode | Version | Précision | FPS | Speed-up |
|-------|----------|---------------|-----------|--------|----------|
| 1 | Mono-GPU | SMART_TENSOR | Float32 | 449 | 1.00x |
| 2 | Mono-GPU | GPU_DEDICATED | Float32 | 501 | 1.12x |
| 3 | Multi-GPU| SMART_TENSOR | Float32 | 511 | 1.14x |
| 4 | Multi-GPU| SMART_TENSOR | Float16 | 664 | 1.48x |
| 5 | Multi-GPU| GPU_DEDICATED | Float32 | 911 | 2.03x |
| 6 | Mono-GPU | SMART_TENSOR | Float16 | 1'215 | 2.71x |
| 7 | Mono-GPU | GPU_DEDICATED | Float16 | 1'618 | 3.60x |
| 8 | Multi-GPU| GPU_DEDICATED | Float16 | 2'104 | 4.69x |

> ℹ️ FPS : number of times the lambda_happy factor is estimated per second.

The test server is equipped with an Intel Xeon E5-2699 v3 processor (2014) and three NVIDIA GeForce RTX 2080 Ti graphics cards (2018).

It uses the default parameters for the evaluation with X of size 1000x1000 and m=10000.

> ℹ️ Note: Use device="cuda" when you create X.

# About This Project

This package, including performance optimizations, was developed as part of a Bachelor’s thesis at HE-Arc by Sevan Yerly (sevan.yerly@he-arc.ch), under the supervision of Cédric Bilat (cedric.bilat@he-arc.ch). The mathematical foundations were developed by Sylvain Sardy (sylvain.sardy@unige.ch).

For questions or contact: sevan.yerly@he-arc.ch or cedric.bilat@he-arc.ch
