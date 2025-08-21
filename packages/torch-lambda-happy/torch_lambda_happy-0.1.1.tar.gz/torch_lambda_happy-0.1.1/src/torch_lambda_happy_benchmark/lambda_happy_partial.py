import torch
from typing import Callable


class LambdaHappyPartial:
    """Stepwise computation of the λ factor for sparse models.

    This helper class breaks down the λ-estimation pipeline into individual
    stages (random projection generation, centering, matrix multiplications,
    norm computations, ratio calculation, and quantile extraction). Users
    can prepare any stage by running all preceding steps via `prepare_func`.
    """

    def __init__(self, X: torch.Tensor, m: int, device_type: str, dtype: torch.dtype):
        """
        Initialize the partial λ-computation pipeline.

        Args:
            X (torch.Tensor): Input tensor of shape (n, p).
            m (int): Number of columns in the random projection matrix Z.
            device_type (str): Target device for computation ('cpu' or 'cuda').
            dtype (torch.dtype): Data type for computation (torch.float32 or torch.float16).
        """
        self._X = X.to(device=device_type, dtype=dtype)
        self._m = m
        self._device_type = device_type
        self._dtype = dtype

        self._Z = None
        self._XTZ = None
        self._numerator = None
        self._denominator = None
        self._lambdas = None

        self.pipeline = [
            self.generate_Z,
            self.center_Z,
            self.compute_XTZ,
            self.compute_numerator,
            self.compute_denominator,
            self.compute_lambdas,
            self.compute_lambda_quantile,
            self.chain1,
            self.chain2,
        ]

    def _get_preparation_pipeline(self, target_func: Callable):
        """Get the list of pipeline steps needed before running `target_func`.

        Args:
            target_func (Callable): One of the methods in `self.pipeline`.

        Raises:
            ValueError: If `target_func` is not found in the pipeline.

        Returns:
            Tuple[List[Callable], Callable]: (preparation steps, the target function)
        """
        if target_func not in self.pipeline:
            raise ValueError(f"Fonction {target_func} non trouvée dans la pipeline")
        idx = self.pipeline.index(target_func)
        return self.pipeline[:idx], target_func

    def prepare_func(self, target_callable: Callable):
        """Execute all pipeline steps prior to the specified target callable.

        Args:
            target_callable (Callable): One of the pipeline methods to prepare for.
        """
        prepare_funcs, _ = self._get_preparation_pipeline(target_callable)
        for func in prepare_funcs:
            func()

    def generate_Z(self):
        """Generate the random projection matrix Z.

        Z has shape (n, m), sampled from a standard normal distribution.
        """
        n = self._X.shape[0]
        self._Z = torch.randn(n, self._m, device=self._device_type, dtype=self._dtype)

    def center_Z(self):
        """Center each column of Z in-place to have zero mean."""
        self._Z.sub_(self._Z.mean(dim=0, keepdim=True))  # In-place centering

    def compute_XTZ(self):
        """Compute the product XᵀZ and store it in `_XTZ`."""
        self._XTZ = self._X.T @ self._Z

    def compute_numerator(self):
        """Compute the Chebyshev (ℓ∞) norm of each column of XᵀZ.

        Stores per-column norms in `_numerator`.
        """
        self._numerator = torch.linalg.norm(self._XTZ, ord=float("inf"), dim=0)

    def compute_denominator(self):
        """Compute the Euclidean (ℓ₂) norm of each column of Z.

        Stores per-column norms in `_denominator`.
        """
        self._denominator = torch.linalg.norm(self._Z, ord=2, dim=0)

    def compute_lambdas(self):
        """Compute the ratio of `_numerator` to `_denominator` for each column.

        Stores results in `_lambdas`.
        """
        self._lambdas = self._numerator / self._denominator

    def compute_lambda_quantile(self) -> float:
        """Compute and return the 0.95-quantile of the λ ratios.

        Returns:
            float: The 0.95-quantile of `_lambdas` (cast to float32).
        """
        return torch.quantile(self._lambdas.to(torch.float32), 0.95).item()

    def chain1(self):
        """Combined step: recompute XᵀZ and its Chebyshev norm.

        Useful for quick re-evaluation without regenerating Z.
        """
        self._XTZ = self._X.T @ self._Z
        self._numerator = torch.linalg.norm(self._XTZ, ord=float("inf"), dim=0)

    def chain2(self) -> float:
        """Full re-evaluation of ratio and quantile, reusing existing Z.

        Returns:
            float: The 0.95-quantile of the recomputed λ ratios.
        """
        self._XTZ = self._X.T @ self._Z
        self._numerator = torch.linalg.norm(self._XTZ, ord=float("inf"), dim=0)
        self._denominator = torch.linalg.norm(self._Z, ord=2, dim=0)
        self._lambdas = self._numerator / self._denominator
        self._lambdas = self._lambdas.to(torch.float32)
        return torch.quantile(self._lambdas, 0.95).item()
