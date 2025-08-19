import argparse
import sys
import pandas as pd
import torch
import matplotlib.pyplot as plt
from lambda_happy import LambdaHappy
from lambda_happy_validation.validation import LambdaValidation
from lambda_happy_validation.dependencies import (
    check_required_dependencies,
    check_optional_dependencies,
)
from lambda_happy_validation.ista_solver import IstaTestRunner


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="CLI for LambdaHappy λ estimation and distribution plotting."
    )
    # Core actions

    parser.add_argument(
        "--distribution_small",
        action="store_true",
        help="Show small-scale λ distribution across multiple m",
    )
    parser.add_argument(
        "--distribution_large",
        action="store_true",
        help="Show large-scale λ distribution across multiple m",
    )

    parser.add_argument(
        "--compute_ista_solver",
        action="store_true",
        help="Run a IstaSolver test with synthetic data",
    )

    parser.add_argument(
        "--compute_multi_ista_solver",
        action="store_true",
        help="Run multiple IstaSolver tests over various p and seeds",
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
        help="Device on which to run (default = torch.cuda if available, else CPU)",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=1_000,
        help="Number of rows in X",
    )
    parser.add_argument(
        "-p",
        type=int,
        default=1_000,
        help="Number of columns (features) in X",
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
        help="Number of runs for distribution plots",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    check_required_dependencies()
    check_optional_dependencies()

    # Map string dtype to torch dtype
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

    # Build random data matrix X
    print(f"> Creating X of shape ({args.n}, {args.p}) on {device} with dtype={dtype}")
    X = torch.randn(args.n, args.p, device=device, dtype=dtype)

    # Instantiate estimator and validation helper
    estimator = LambdaHappy(X)
    # Pass interactive flag to LambdaValidation for backend selection
    bench = LambdaValidation(estimator)

    any_action = False

    # Compute single λ estimate
    if args.compute_lambda:
        lam = estimator.compute(
            m=args.m,
            device_type=device,
            dtype=dtype,
        )
        print(f"> λ estimate (m={args.m}): {lam:.6f}")
        any_action = True

    # Small-scale λ distribution
    if args.distribution_small:
        print("> Showing small λ distribution…")
        bench.show_lambda_distribution_small(
            nb_run=args.nb_runs,
        )
        any_action = True

    # Large-scale λ distribution
    if args.distribution_large:
        print("> Showing large λ distribution…")
        bench.show_lambda_distribution_large(
            nb_run=args.nb_runs,
        )
        any_action = True

    if args.compute_ista_solver:
        print(
            f"> Running IstaSolver with n={args.n}, p={args.p}, device={device}, dtype={dtype}"
        )
        runner = IstaTestRunner(device_type=device, dtype=dtype)
        result = runner.run_test(n=args.n, p=args.p, seed=0)
        print("IstaSolver Test Result:")
        print(f"  - Support match:     {result['support_match']}")
        print(f"  - MSE:               {result['mse']:.6f}")
        print(f"  - True support:      {result['true_nonzero_idx']}")
        print(f"  - Estimated support: {result['est_nonzero_idx']}")
        print(f"  - True values:       {result['true_vals']}")
        print(f"  - Estimated values:  {result['est_vals']}")
        any_action = True

    if args.compute_multi_ista_solver:
        print("> Running multiple IstaSolver tests over various p and seeds...")
        istaTestRunner = IstaTestRunner(
            device_type=device, dtype=dtype
        )

        p_list = [100, 200, 500, 1_000]
        seeds = [0, 1, 2, 3, 4]

        istaTestRunner.run_all(p_list, seeds)
        any_action = True

    if not any_action:
        print("No action requested. Use --help to see available options.")
        sys.exit(1)

    # Display any open figures
    if plt.get_fignums():
        plt.show()


if __name__ == "__main__":
    main()
