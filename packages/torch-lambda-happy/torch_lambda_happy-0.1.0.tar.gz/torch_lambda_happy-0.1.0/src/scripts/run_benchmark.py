import argparse
import sys

import torch
from lambda_happy import LambdaHappy
from lambda_happy_benchmark.benchmark import LambdaBenchmark

from lambda_happy_benchmark.dependencies import (
    check_required_dependencies,
    check_optional_dependencies,
)

import matplotlib.pyplot as plt


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
        help="Compute a single λ estimate and print it",
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
        "--nb_runs",
        type=int,
        default=500,
        help="Number of runs for batched benchmarks / distributions",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    check_required_dependencies()
    check_optional_dependencies()

    dtype_map = {
        "float16": torch.float16,
        "float32": torch.float32,
    }
    dtype = dtype_map[args.dtype]

    # Determine device
    if args.device:
        device = args.device
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
        lam = estimator.compute(
            m=args.m, device_type=device, dtype=dtype
        )
        print(f"> λ estimate (m={args.m}): {lam:.6f}")
        any_ran = True

    if args.benchmark_2D:
        print("> Running 2D benchmark…")
        bench.show_benchmark_2D(
        )
        any_ran = True

    if args.benchmark_3D:
        print("> Running 3D benchmark…")
        bench.show_benchmark_3D(
        )
        any_ran = True

    if args.benchmark_float:
        print("> Running float16 vs float32 benchmark on CUDA…")
        bench.show_benchmark_float(
        )
        any_ran = True

    if args.benchmark_format:
        print("> Running format conversion benchmark…")
        bench.show_benchmark_format_conversion(n=args.n, p=args.p, m=args.m)
        any_ran = True

    if args.benchmark_partial:
        print("> Running partial benchmark (LambdaHappyPartial)…")
        bench.benchmark_partial(n=args.n, p=args.p, m=args.m, nb_run=args.nb_runs)
        any_ran = True

    if not any_ran:
        print("No action requested. Use --help to see available options.")
        sys.exit(1)

    if plt.get_fignums():
        plt.show()


if __name__ == "__main__":
    main()
