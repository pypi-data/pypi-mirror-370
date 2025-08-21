import torch
import time
import pytest

from torch_lambda_happy import LambdaHappy


@pytest.fixture(scope="module", params=["cpu", "cuda"])
def X(request):
    device = request.param
    if device == "cuda" and not torch.cuda.is_available():
        pytest.skip("CUDA is not available on this machine.")
    torch.manual_seed(0)
    return torch.randn(50, 100, dtype=torch.float32, device=device)


class TestLambdaHappy:

    @pytest.mark.parametrize("method", ["compute", "compute_agg", "compute_many"])
    def test_return_types(self, X, method):
        model = LambdaHappy(X)
        if method == "compute":
            val = model.compute()
            assert isinstance(val, float)
        elif method == "compute_agg":
            val = model.compute_agg(nb_run=10)
            assert isinstance(val, float)
        elif method == "compute_many":
            val = model.compute_many(nb_run=10)
            assert isinstance(val, list)
            assert all(isinstance(v, float) for v in val)

    def test_device_and_dtype_are_immutable_after_model_init(self, X):
        model = LambdaHappy(X)

        assert model.get_device_type() == X.device.type
        assert model.get_dtype() == X.dtype

        new_dtype = torch.float16 if X.dtype == torch.float32 else torch.float32
        X = X.to(new_dtype)
        assert model.get_dtype() != X.dtype

        new_device = "cpu" if X.device.type == "cuda" else "cuda"
        if new_device == "cuda" and not torch.cuda.is_available():
            pytest.skip("CUDA is not available on this machine.")
        X = X.to(new_device)
        assert model.get_device_type() != X.device.type

    def test_variance_decreases_when_m_increases(self, X):
        model = LambdaHappy(X)
        vals_small_m = model.compute_many(nb_run=50, m=100)
        vals_medium_m = model.compute_many(nb_run=50, m=1_000)
        vals_large_m = model.compute_many(nb_run=50, m=10_000)

        var_small = torch.tensor(vals_small_m).var().item()
        var_medium = torch.tensor(vals_medium_m).var().item()
        var_large = torch.tensor(vals_large_m).var().item()

        assert var_medium < var_small
        assert var_large < var_small
        assert var_large < var_medium

    def test_compute_many_returns_correct_length(self, X):
        model = LambdaHappy(X)
        nb_run = 10
        results = model.compute_many(nb_run=nb_run)
        assert isinstance(results, list)
        assert len(results) == nb_run
        assert all(isinstance(x, float) for x in results)

    def test_agg_matches_manual_aggregation(self, X):
        model = LambdaHappy(X)
        vals = model.compute_many(nb_run=500)
        agg1 = torch.median(torch.tensor(vals)).item()
        agg2 = model.compute_agg(nb_run=500, func=torch.median)
        assert abs(agg1 - agg2) < 1e-1

    def test_float16_is_faster_than_float32_on_cuda(self):
        if not torch.cuda.is_available():
            pytest.skip("CUDA is not available on this machine.")

        torch.manual_seed(42)
        X_fp32 = torch.randn(1000, 1000, dtype=torch.float32, device="cuda")
        X_fp16 = X_fp32.to(dtype=torch.float16)

        model_fp32 = LambdaHappy(X_fp32)
        model_fp16 = LambdaHappy(X_fp16)

        # Warm-up CUDA to avoid initialization overhead
        model_fp32.compute()
        model_fp16.compute()

        # Time float32
        torch.cuda.synchronize()
        start_fp32 = time.time()
        model_fp32.compute_many(nb_run=500, dtype=torch.float32)
        torch.cuda.synchronize()
        duration_fp32 = time.time() - start_fp32

        # Time float16
        torch.cuda.synchronize()
        start_fp16 = time.time()
        model_fp16.compute_many(nb_run=500, dtype=torch.float16)
        torch.cuda.synchronize()
        duration_fp16 = time.time() - start_fp16

        print(f"float32 duration: {duration_fp32:.4f}s")
        print(f"float16 duration: {duration_fp16:.4f}s")

        assert duration_fp16 < duration_fp32

    @pytest.mark.skipif(
        not torch.cuda.is_available() or torch.cuda.device_count() < 2,
        reason="Requires at least 2 GPUs",
    )
    def test_multigpu_behavior(self):
        torch.manual_seed(123)
        Xd = torch.randn(1000, 1000, dtype=torch.float32, device="cuda")
        model_multi = LambdaHappy(Xd, force_fastest=True, use_multigpu=True)
        model_single = LambdaHappy(Xd, force_fastest=True, use_multigpu=False)

        # Check that results are of the correct type
        result_multi = model_multi.compute_agg(nb_run=20)
        result_single = model_single.compute_agg(nb_run=20)

        assert isinstance(result_multi, float)
        assert isinstance(result_single, float)

        # Compare the results (allowing some tolerance since multigpu can vary slightly)
        assert abs(result_multi - result_single) < 1e-1

        # Optional: check that multiple GPUs are used if LambdaHappy exposes such info
        if hasattr(model_multi, "get_devices_used"):
            devices = model_multi.get_devices_used()
            assert len(devices) > 1
