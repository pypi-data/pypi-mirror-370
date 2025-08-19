from datetime import datetime
from typing import List

import torch
import numpy as np
import matplotlib

from lambda_happy import LambdaHappy


def choose_matplotlib_backend(interactive: bool = False) -> str:
    """Selects and sets an available matplotlib backend.

    Args:
        interactive (bool, optional): If True, prefer interactive backends.

    Raises:
        RuntimeError: If no suitable backend is found.

    Returns:
        str: The name of the selected backend.
    """
    preferred_backends = (
        ["Qt5Agg", "TkAgg", "Agg"] if interactive else ["Agg", "Qt5Agg", "TkAgg"]
    )
    for backend in preferred_backends:
        try:
            matplotlib.use(backend, force=True)
            print(f"[matplotlib] Using backend: {backend}")
            return backend
        except ImportError:
            continue
    raise RuntimeError("No suitable matplotlib backend found.")


class LambdaValidation:
    """Validation and plotting utilities for LambdaHappy estimators."""

    def __init__(self, estimator: LambdaHappy, interactive: bool = False):
        """Initializes with estimator and sets up matplotlib backend.

        Args:
            estimator (LambdaHappy): Estimator to validate.
            interactive (bool, optional): Use interactive plotting if True. Defaults to False.
        """
        self.estimator = estimator

        self.dtype_map = {torch.float32: "f32", torch.float16: "f16"}

        # Set matplotlib backend according to interactive flag
        self.backend = choose_matplotlib_backend(interactive)
        import matplotlib.pyplot as plt

        self.plt = plt

        self.USE_AGG = self.backend.lower() == "agg"

    def _finalize_plot(
        self,
        fig,
        name: str,
        params: dict = None,
        device: str = None,
        dtype: str = None,
        output_dir: str = ".",
    ):
        """Saves or shows a matplotlib figure depending on backend.

        Args:
            fig: Matplotlib figure.
            name (str): Base name of the output file.
            params (dict, optional): Parameters to include in the filename.
            device (str, optional): Device info for filename.
            dtype (str, optional): Dtype info for filename.
            output_dir (str, optional): Directory to save figure.
        """
        if params is None:
            params = {}

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        params_part = "_".join(f"{str(v)}" for _, v in params.items())
        device_part = f"_{device}" if device else ""
        dtype_part = f"_{dtype}" if dtype else ""
        params_part = f"_{params_part}" if params_part else ""

        filename = (
            f"{output_dir}/"
            f"{name}"
            f"{params_part.lower()}"
            f"{device_part.lower()}{dtype_part.lower()}"
            f"_{timestamp}.png"
        )

        if self.USE_AGG:
            fig.savefig(filename, dpi=300, bbox_inches="tight")
            print(f"[Agg] figure saved as {filename}")
            self.plt.close(fig)
        else:
            self.plt.show(block=False)
            self.plt.pause(0.1)

    def _estimate_lambda_distribution(
        self, m_values: np.ndarray, nb_run: int = 100
    ) -> List[List[float]]:
        """Computes multiple lambda estimates for a range of m values.

        Args:
            m_values (np.ndarray): Array of m values to test.
            nb_run (int, optional): Number of estimations per m. Defaults to 100.

        Returns:
            List[List[float]]: List of lambda estimations for each m.
        """
        results = []
        for m in m_values:
            results.append(
                self.estimator.compute_many(nb_run=nb_run, m=m)
            )
        return results

    def _show_lambda_distribution(
        self,
        median_value: float,
        results: List[List[float]],
        m_values: np.ndarray,
        m_median_size: int = 100_000,
        title: str = "small",
    ) -> None:
        """Plots lambda distribution and variance for different m values.

        Args:
            median_value (float): Reference median value to plot.
            results (List[List[float]]): Lambda estimates grouped by m.
            m_values (np.ndarray): Array of m values used.
            m_median_size (int, optional): Size used to compute reference median. Defaults to 100_000.
            title (str, optional): Title label for the plot. Defaults to "small".
        """
        formatted_median_size = f"{m_median_size:,}".replace(",", "_")

        fig, (ax1, ax2) = self.plt.subplots(1, 2, figsize=(16, 6))
        n, p = self.estimator.X.shape
        fig.suptitle(
            f"Lambda Estimations : Distribution and Variance aross {title} m values\n"
            f"({n=}, {p=}, device={self.estimator.get_device_type()}, dtype={self.dtype_map.get(self.estimator.get_dtype())})",
            fontsize=14,
        )

        ax1.boxplot(results, positions=range(1, len(m_values) + 1))
        ax1.set_xticks(range(1, len(m_values) + 1))
        ax1.set_xticklabels(m_values)
        ax1.set_xlabel("m Size")
        ax1.set_ylabel("Lambda values distribution")
        ax1.hlines(
            median_value,
            1,
            len(m_values),
            linestyles="dashed",
            colors="red",
            label=f"Median (m size : {formatted_median_size}): {median_value:.5f}",
        )

        ax2.plot(
            range(1, len(m_values) + 1),
            [np.var(i) for i in results],
            color="blue",
            label="Variance",
        )
        ax2.set_xticks(range(1, len(m_values) + 1))
        ax2.set_xticklabels(m_values)
        ax2.set_ylabel("Variance")
        ax2.set_xlabel("m Size")

        ax1.legend(loc="upper right")
        ax2.legend(loc="upper right")

        ax1.grid(True)
        ax2.grid(True)

        self.plt.tight_layout()
        self._finalize_plot(
            fig,
            name="lambda_distribution",
            device=self.estimator.get_device_type(),
            dtype=self.dtype_map.get(self.estimator.get_dtype()),
        )

    def show_lambda_distribution_small(
        self,
        m_values: np.ndarray = None,
        nb_run: int = 100,
        m_median_size: int = 100_000,
    ) -> None:
        """Displays lambda distribution plot for small m values.

        Args:
            m_values (np.ndarray, optional): m values to test. Defaults to powers of 2 from 10 to 10K.
            nb_run (int, optional): Number of estimations per m. Defaults to 100.
            m_median_size (int, optional): Size used to compute reference median. Defaults to 100_000.
        """

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        results = self._estimate_lambda_distribution(
            m_values, nb_run=nb_run
        )
        median_value = self.estimator.compute_agg(
            nb_run=nb_run, func=torch.median, m=m_median_size
        )

        self._show_lambda_distribution(
            median_value=median_value,
            results=results,
            m_values=m_values,
            m_median_size=m_median_size,
            title="small",
        )

    def show_lambda_distribution_large(
        self,
        m_values: np.ndarray = None,
        nb_run: int = 100,
        m_median_size: int = 100_000,
    ) -> None:
        """Displays lambda distribution plot for large m values.

        Args:
            m_values (np.ndarray, optional): Large m values to test. Defaults to range ~10K–300K.
            nb_run (int, optional): Number of estimations per m. Defaults to 100.
            m_median_size (int, optional): Size used to compute reference median. Defaults to 100_000.
        """

        if m_values is None:
            m_values = np.concatenate(
                (
                    10 * 2 ** np.arange(10, 14),
                    (
                        (10 * 2 ** np.arange(10, 14) + 10 * 2 ** np.arange(11, 15)) / 2
                    ).astype(int),
                )
            )
        m_values.sort()

        results = self._estimate_lambda_distribution(
            m_values, nb_run=nb_run
        )
        median_value = self.estimator.compute_agg(
            nb_run=nb_run, func=torch.median, m=m_median_size
        )

        self._show_lambda_distribution(
            median_value=median_value,
            results=results,
            m_values=m_values,
            m_median_size=m_median_size,
            title="large",
        )
