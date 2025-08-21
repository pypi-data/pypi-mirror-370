import argparse
import sys
import time

from lambda_happy_benchmark.dependencies import (
    check_required_dependencies,
    check_optional_dependencies,
)

check_required_dependencies()
check_optional_dependencies()

import torch

from lambda_happy import LambdaHappy
from lambda_happy_benchmark.benchmark import LambdaBenchmark
from .utils import choose_matplotlib_backend


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="CLI for LambdaHappy benchmarking and λ estimation."
    )
    # Benchmark toggles
    parser.add_argument(
        "--benchmark_2D", action="store_true", help="Run 2D benchmark (m vs throughput)"
    )
    parser.add_argument(
        "--benchmark_3D",
        action="store_true",
        help="Run 3D benchmark (m,p vs throughput)",
    )
    parser.add_argument(
        "--benchmark_float",
        action="store_true",
        help="Compare CUDA float16 vs float32 throughput",
    )
    parser.add_argument(
        "--benchmark_version",
        action="store_true",
        help="Compare GPU_DEDICATED vs SMART_TENSOR on CUDA",
    )
    parser.add_argument(
        "--benchmark_format",
        action="store_true",
        help="Compare format conversion (float32/16 CPU/CUDA)",
    )

    parser.add_argument(
        "--benchmark_partial",
        action="store_true",
        help="Benchmark each partial step of LambdaHappyPartial",
    )

    parser.add_argument(
        "--compute_lambda",
        action="store_true",
        help="Estimate lambda using multiple runs (--nb_run) and display the result with performance (FPS).",
    )

    # Hyper‑parameters
    parser.add_argument(
        "--dtype",
        type=str,
        default="float32",
        choices=["float16", "float32"],
        help="Tensor data type for computation",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="SMART_TENSOR",
        choices=["AUTOMATIC", "GPU_DEDICATED", "SMART_TENSOR"],
        help="Implementation version to use",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        choices=["cpu", "cuda"],
        help="Device on which to run (default = X.device or cpu if not set)",
    )
    parser.add_argument("-n", type=int, default=1_000, help="Number of rows in X")
    parser.add_argument(
        "-p", type=int, default=1_000, help="Number of columns (features) in X"
    )
    parser.add_argument(
        "-m",
        type=int,
        default=10_000,
        help="Number of random projection vectors (columns of Z)",
    )
    parser.add_argument(
        "--nb_run",
        type=int,
        default=500,
        help="Number of runs to average results (applies only to --compute_lambda, --benchmark_partial and --benchmark_float).",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enables interactive backend like Qt5Agg for matplotlib",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    choose_matplotlib_backend(args.interactive)
    import matplotlib.pyplot as plt

    dtype_map = {
        "float16": torch.float16,
        "float32": torch.float32,
    }
    dtype = dtype_map[args.dtype]

    # Determine device
    if args.device:
        device = args.device
        if torch.cuda.is_available() == False:
            device = "cpu"
            print(f"> Cuda is not available, using cpu instead")
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # Build random X
    print(f"> Creating X of shape ({args.n}, {args.p}) on {device} with dtype={dtype}")
    X = torch.randn(args.n, args.p, device=device, dtype=dtype)

    # Instantiate
    estimator = LambdaHappy(X)
    bench = LambdaBenchmark(estimator)

    # Dispatch
    any_ran = False

    if args.compute_lambda:
        if estimator.get_device_type() == "cuda" and torch.cuda.is_available():
            torch.cuda.synchronize()
        start = time.perf_counter()
        lambdas = estimator.compute_agg(
            nb_run=args.nb_run,
            m=args.m,
            version=args.version,
            device_type=device,
            dtype=dtype,
        )
        if estimator.get_device_type() == "cuda" and torch.cuda.is_available():
            torch.cuda.synchronize()

        print(
            f"> λ estimate (m={args.m}, nb_run={args.nb_run}, version={args.version}): {lambdas:.6f} (FPS: {args.nb_run / (time.perf_counter() - start)})"
        )
        any_ran = True

    if args.benchmark_2D:
        print("> Running 2D benchmark…")
        bench.show_benchmark_2D(n=args.n, p=args.p, m=args.m, version=args.version)
        any_ran = True

    if args.benchmark_3D:
        print("> Running 3D benchmark…")
        bench.show_benchmark_3D(
            n=args.n,
            version=args.version,
        )
        any_ran = True

    if args.benchmark_float:
        print("> Running float16 vs float32 benchmark on CUDA…")
        bench.show_benchmark_float(version=args.version, nb_run=args.nb_run)
        any_ran = True

    if args.benchmark_version:
        print("> Running version comparison benchmark on CUDA…")
        bench.show_benchmark_version()
        any_ran = True

    if args.benchmark_format:
        print("> Running format conversion benchmark…")
        bench.show_benchmark_format_conversion(n=args.n, p=args.p, m=args.m)
        any_ran = True

    if args.benchmark_partial:
        print("> Running partial benchmark (LambdaHappyPartial)…")
        bench.benchmark_partial(n=args.n, p=args.p, m=args.m, nb_run=args.nb_run)
        any_ran = True

    if not any_ran:
        print("No action requested. Use --help to see available options.")
        sys.exit(1)

    if plt.get_fignums():
        plt.show()


if __name__ == "__main__":
    main()
