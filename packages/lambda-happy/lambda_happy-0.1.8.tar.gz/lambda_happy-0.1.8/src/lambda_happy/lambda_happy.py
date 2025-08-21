import torch
from typing import List, Callable, Optional

from .lib_lambda import (
    LambdaComputerF32,
    LambdaComputerF16,
    MultiLambdaComputerF16,
    MultiLambdaComputerF32,
)


class LambdaHappy:
    """Compute the λ factor for solving sparse models on CPU or GPU.

    LambdaHappy estimates a scalar λ by projecting a (possibly sparse) tensor
    onto random subspaces and taking the 0.95-quantile of the ratio between
    the Chebyshev norm of XᵀZ and the l2-norm of Z. Backends include native
    C++ CUDA kernels and PyTorch routines on both CPU and GPU.

    Examples:

        # Recommended usecase (single estimation)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1_000, 1_000, device="cuda")  # Already in cuda
        >>> model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=True)
        >>> lambda_ = model.compute(m=10_000)
        >>> print(f"Estimated λ: {lambda_:.4f}")

        # Recommended usecase (many estimations)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1_000, 1_000, device="cuda")  # Already in cuda
        >>> model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=True)
        >>> lambda_ = model.compute_many(m=10_000, nb_run=100)
        >>> print(f"Estimated λs: {lambda_}")

        # Recommended usecase (aggregated estimation)
        >>> import torch
        >>> from lambda_happy import LambdaHappy
        >>> matX = torch.randn(1_000, 1_000, device="cuda")  # Already in cuda
        >>> model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=True)
        >>> lambda_ = model.compute_agg(m=10_000, nb_run=100, func=torch.mean)
        >>> print(f"Estimated λ: {lambda_:.4f}")

        # With minimal parameters (single estimation)
        >>> matX = torch.randn(1_000, 1_000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda_ = model.compute()
        >>> print(f"Estimated λ: {lambda_:.4f}")

        # With all parameters (single estimation)
        >>> matX = torch.randn(1_000, 1_000)
        >>> model = LambdaHappy(X=matX, force_fastest=False, use_multigpu=False)
        >>> lambda_ = model.compute(m=10_000, version="AUTOMATIC",
                                    dtype=torch.float16, device_type="cuda")
        >>> print(f"Estimated λ: {lambda_:.4f}")

        # With minimal parameters (many estimations)
        >>> matX = torch.randn(1_000, 1_000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda_ = model.compute_many(nb_run=100)
        >>> print(f"Estimated λs: {lambda_}")

        # With all parameters (many estimations)
        >>> matX = torch.randn(1_000, 1_000)
        >>> model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=False)
        >>> lambda_ = model.compute_many(m=10_000, version="AUTOMATIC",
                                        dtype=torch.float32, device_type="cuda", nb_run=100)
        >>> print(f"Estimated λs: {lambda_}")

        # With minimal parameters (aggregated estimation)
        >>> matX = torch.randn(1_000, 1_000)
        >>> model = LambdaHappy(X=matX)
        >>> lambda_ = model.compute_agg(nb_run=100)
        >>> print(f"Estimated λ: {lambda_:.4f}")

        # With all parameters (aggregated estimation)
        >>> matX = torch.randn(1_000, 1_000)
        >>> model = LambdaHappy(X=matX, force_fastest=True, use_multigpu=True)
        >>> lambda_ = model.compute_agg(m=10_000, version="AUTOMATIC",
                                       dtype=torch.float32, device_type="cpu",
                                       nb_run=100, func=torch.mean)
        >>> print(f"Estimated λ: {lambda_:.4f}")
    """

    __slots__ = (
        "__X_cache",
        "__use_multigpu",
        "__cuda_worker_f16",
        "__cuda_worker_f32",
    )

    VALID_VERSIONS = {"AUTOMATIC", "GPU_DEDICATED", "SMART_TENSOR"}

    __dispatch_default = {
        ("cuda", torch.float32): lambda self, m: self._gpu_f32_native(m),
        ("cuda", torch.float16): lambda self, m: self._gpu_f16_native(m),
        ("cpu", torch.float32): lambda self, m: self._cpu_f32_pytorch(m),
        ("cpu", torch.float16): lambda self, m: self._cpu_f16_pytorch(m),
    }
    __dispatch_native = {
        ("cuda", torch.float32): lambda self, m: self._gpu_f32_native(m),
        ("cuda", torch.float16): lambda self, m: self._gpu_f16_native(m),
        ("cpu", torch.float32): lambda self, m: self._cpu_f32_pytorch(m),
        ("cpu", torch.float16): lambda self, m: self._cpu_f16_pytorch(m),
    }
    __dispatch_pytorch = {
        ("cuda", torch.float32): lambda self, m: self._gpu_f32_pytorch(m),
        ("cuda", torch.float16): lambda self, m: self._gpu_f16_pytorch(m),
        ("cpu", torch.float32): lambda self, m: self._cpu_f32_pytorch(m),
        ("cpu", torch.float16): lambda self, m: self._cpu_f16_pytorch(m),
    }

    def __init__(
        self, X: torch.Tensor, force_fastest: bool = False, use_multigpu: bool = False
    ):
        """Initialize the LambdaHappy solver.

        Args:
            X (torch.Tensor): Input tensor of shape (n, p).
            force_fastest (bool, optional): If True, converts and stores X in the most efficient
                                            available format:
                                                - CUDA + float16 if available
                                                - Otherwise CPU + float32
                                            This ensures conversions are done once at initialization.
                                            Defaults to False.
            use_multigpu (bool, optional): If True, attempts to use all available CUDA GPUs
                                           Defaults to False.
        Note:
            Usage examples are provided in the class-level docstring of `LambdaHappy`.
        """

        self.__use_multigpu = use_multigpu
        if torch.cuda.device_count() <= 1:
            self.__use_multigpu = False

        self.__X_cache = {}

        if force_fastest:
            if torch.cuda.is_available():
                X_opt = X.to(device="cuda", dtype=torch.float16).contiguous()
            else:
                X_opt = X.to(device="cpu", dtype=torch.float32).contiguous()
        else:
            X_opt = X.contiguous()

        self.__X_cache[(X_opt.device.type, X_opt.dtype)] = X_opt

        self.__X_cache["default"] = X_opt

        if torch.cuda.is_available():
            try:
                _ = torch.empty(1, device="cuda")
                device_index = self.__X_cache["default"].device.index or 0
                seed = torch.cuda.default_generators[device_index].initial_seed()
                worker_f16 = (
                    MultiLambdaComputerF16(seed=seed)
                    if use_multigpu
                    else LambdaComputerF16(seed=seed)
                )
                worker_f32 = (
                    MultiLambdaComputerF32(seed=seed)
                    if use_multigpu
                    else LambdaComputerF32(seed=seed)
                )
            except Exception:
                worker_f16 = None
                worker_f32 = None

        self.__cuda_worker_f16 = worker_f16
        self.__cuda_worker_f32 = worker_f32

    @property
    def X(self) -> torch.Tensor:
        """Returns a copy of the default version of the internal X tensor.

        Returns:
            torch.Tensor: A cloned tensor of the default cached X.
        """
        return self.__X_cache["default"].clone()

    def _validate_args(
        self, m: int, version: str, device_type: str, dtype: torch.dtype
    ):
        """Validate basic arguments for solver setup.

        Args:
            m (int): Must be > 0.
            version (str): Must be in self.VALID_VERSIONS.
            device_type (str): 'cpu' or 'cuda'.
            dtype (torch.dtype): torch.float32 or torch.float16.

        Raises:
            ValueError, RuntimeError: If any argument is invalid.
        """
        if m <= 0:
            raise ValueError(f"Invalid m: {m}, expected : m >= 0")
        if version not in self.VALID_VERSIONS:
            raise ValueError(
                f"Invalid version: {version}, expected : {self.VALID_VERSIONS}"
            )
        if device_type not in ("cpu", "cuda"):
            raise ValueError(f"Invalid device_type: {device_type}")
        if dtype not in (torch.float32, torch.float16):
            raise ValueError(f"Invalid dtype: {dtype}")
        if device_type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA not available")

    def _select_impl(
        self, version: str, device_type: str, dtype: torch.dtype
    ) -> Callable[[int], float]:
        """Select the computation implementation based on parameters.

        Args:
            version (str): Execution mode.
            device_type (str): 'cpu' or 'cuda'.
            dtype (torch.dtype): Desired tensor data type.

        Raises:
            RuntimeError: If no implementation matches the given settings.

        Returns:
            Callable[[int], float]: Function taking m and returning λ.
        """
        key = (device_type, dtype)
        if version == "AUTOMATIC":
            fn = self.__dispatch_default.get(key)
        elif version == "GPU_DEDICATED":
            fn = self.__dispatch_native.get(key)
        elif version == "SMART_TENSOR":
            fn = self.__dispatch_pytorch.get(key)

        if fn is None:
            raise RuntimeError(
                f"No implementation for ({device_type =}, {dtype =} and {version =})"
            )
        return fn

    def _get_converted_X(self, device: str, dtype: torch.dtype) -> torch.Tensor:
        """Return the cached or converted version of the input tensor X.

        If a version of X matching the given device and dtype is not yet cached,
        this method will convert the default X tensor to the requested format,
        store it in the cache, and return it.

        Args:
            device (str): Target device ('cpu' or 'cuda').
            dtype (torch.dtype): Desired data type (e.g., torch.float32, torch.float16).

        Returns:
            torch.Tensor: Tensor X on the requested device and dtype, cached for reuse.
        """
        key = (device, dtype)
        if key not in self.__X_cache:
            self.__X_cache[key] = (
                self.__X_cache["default"].to(device=device, dtype=dtype).contiguous()
            )
        return self.__X_cache[key]

    def compute(
        self,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        """Compute a single estimate of λ.

        Args:
            m (int, optional): Number of columns in the random projection matrix Z.
                    Z has shape (n, m). Defaults to 10000.
            version (str, optional): Strategy for dispatching the λ-computation. Must be one of:
                    - 'AUTOMATIC': automatically picks the best available backend for the current
                    device and dtype (either native C++ CUDA or PyTorch routines).
                    - 'GPU_DEDICATED': always uses the native C++ CUDA implementation on GPU;
                    raises if no CUDA float implementation is available.
                    - 'SMART_TENSOR': runs via PyTorch on CPU or GPU with smart tensor
                    optimizations (mixed-precision, fused ops).
                    Defaults to 'AUTOMATIC'.
            device_type (str, optional): 'cpu' or 'cuda'. Defaults to X.device.type.
            dtype (torch.dtype, optional): Data type for computation. Defaults to X.dtype.

        Returns:
            float: The estimated λ (0.95-quantile).
        """
        device_type = device_type or self.__X_cache["default"].device.type
        dtype = dtype or self.__X_cache["default"].dtype

        self._validate_args(m, version, device_type, dtype)
        impl = self._select_impl(version, device_type, dtype)
        return impl(self, m)

    def compute_many(
        self,
        nb_run: int,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> List[float]:
        """
        Compute multiple independent estimates of λ.

        Args:
            nb_run (int): Number of independent runs.
            m (int, optional): Number of columns in the random projection matrix Z.
                    Z has shape (n, m). Defaults to 10000.
            version (str, optional): Strategy for dispatching the λ-computation. Must be one of:
                    - 'AUTOMATIC': automatically picks the best available backend for the current
                    device and dtype (either native C++ CUDA or PyTorch routines).
                    - 'GPU_DEDICATED': always uses the native C++ CUDA implementation on GPU;
                    raises if no CUDA float implementation is available.
                    - 'SMART_TENSOR': runs via PyTorch on CPU or GPU with smart tensor
                    optimizations (mixed-precision, fused ops).
                    Defaults to 'AUTOMATIC'.
            device_type (str, optional): 'cpu' or 'cuda'. Defaults to X.device.type.
            dtype (torch.dtype, optional): Data type for computation.
                                           Defaults to X.dtype.

        Returns:
            List[float]: A list of λ estimates, one per run.
        """
        device_type = device_type or self.__X_cache["default"].device.type
        dtype = dtype or self.__X_cache["default"].dtype
        self._validate_args(m, version, device_type, dtype)
        impl = self._select_impl(version, device_type, dtype)
        return [impl(self, m) for _ in range(nb_run)]

    def compute_agg(
        self,
        nb_run: int,
        func: Callable = torch.median,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        """Compute an aggregated λ estimate over multiple runs.

        Args:
            nb_run (int): Number of independent runs.
            func (Callable, optional): Aggregation function (e.g., torch.mean,
                                       torch.median). Defaults to torch.median.
            m (int, optional): Number of columns in the random projection matrix Z.
                    Z has shape (n, m). Defaults to 10000.
            version (str, optional): Strategy for dispatching the λ-computation. Must be one of:
                    - 'AUTOMATIC': automatically picks the best available backend for the current
                    device and dtype (either native C++ CUDA or PyTorch routines).
                    - 'GPU_DEDICATED': always uses the native C++ CUDA implementation on GPU;
                    raises if no CUDA float implementation is available.
                    - 'SMART_TENSOR': runs via PyTorch on CPU or GPU with smart tensor
                    optimizations (mixed-precision, fused ops).
                    Defaults to 'AUTOMATIC'.
            device_type (str, optional): 'cpu' or 'cuda'. Defaults to X.device.type.
            dtype (torch.dtype, optional): Data type for computation.
                                           Defaults to X.dtype.

        Returns:
            float: Aggregated λ estimate (result of func over individual runs).
        """
        device_type = device_type or self.__X_cache["default"].device.type
        dtype = dtype or self.__X_cache["default"].dtype
        self._validate_args(m, version, device_type, dtype)
        impl = self._select_impl(version, device_type, dtype)

        results = torch.empty(nb_run, dtype=dtype, device=device_type)
        for i in range(nb_run):
            results[i] = impl(self, m)

        return func(results).item()

    def get_dtype(self) -> torch.dtype:
        """Get the data type of the input tensor X.

        Returns:
            torch.dtype: The dtype of X.
        """
        return self.__X_cache["default"].dtype

    def get_device_type(self) -> str:
        """Get the device type of the input tensor X.

        Returns:
            str: 'cpu' or 'cuda'.
        """
        return self.__X_cache["default"].device.type

    def _gpu_f32_native(self, m: int) -> float:
        """Compute λ using the native CUDA float32 backend.

        Args:
            m (int): Number of columns in Z.

        Raises:
            RuntimeError: If the native CUDA backend is not available.

        Returns:
            float: Estimated λ.
        """
        if self.__cuda_worker_f32 is None:
            raise RuntimeError("Native CUDA backend not available")
        Xc = self._get_converted_X("cuda", torch.float32)
        return self.__cuda_worker_f32.compute(Xc, m)

    def _gpu_f16_native(self, m: int) -> float:
        """Compute λ using the native CUDA float16 backend.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        if self.__cuda_worker_f16 is None:
            raise RuntimeError("Native CUDA backend not available")
        Xc = self._get_converted_X("cuda", torch.float16)
        return self.__cuda_worker_f16.compute(Xc, m)

    def _gpu_f32_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CUDA with float32.

        Args:
            m (int): Number of columns in Z.

        Raises:
            RuntimeError: If the native CUDA backend is not available.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cuda", torch.float32)

    def _gpu_f16_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CUDA with float16.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cuda", torch.float16)

    def _cpu_f32_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CPU with float32.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cpu", torch.float32)

    def _cpu_f16_pytorch(self, m: int) -> float:
        """Compute λ via PyTorch routines on CPU with float16.

        Args:
            m (int): Number of columns in Z.

        Returns:
            float: Estimated λ.
        """
        return self._pytorch_compute(m, "cpu", torch.float16)

    def _pytorch_compute(self, m: int, device: str, dtype: torch.dtype) -> float:
        """Estimate λ using randomized PyTorch.

        Computes λ = ||XᵀZ||_∞ / ||Z||₂, where:
            - ||·||∞ is the Chebyshev norm over each column.
            - Z ~ N(0, 1) ∈ ℝⁿˣᵐ is column-wise zero-centered.

        Steps:
            1. Sample Z ~ N(0, 1) of shape (n, m) and center columns.
            2. Move X and Z to the given device and dtype.
            3. Compute:
                - numer = ||XᵀZ||∞ : Chebyshev norm per projected column.
                - denom = ||Z||₂ : l2 norm per column.
            4. Compute λ = numer / denom element-wise.
            5. Return the 0.95-quantile of the λ values.

        Multi-GPU: If enabled and available, splits computation across GPUs using CUDA streams.

        Args:
            m (int): Number of random projections.
            device (str): 'cpu' or 'cuda'.
            dtype (torch.dtype): Precision for computation.

        Returns:
            float: Estimated λ (0.95-quantile of computed ratios).
        """
        if device == "cpu" or not self.__use_multigpu or not torch.cuda.is_available():
            # Fallback to single-device if no multiple GPUs
            X = self._get_converted_X(device=device, dtype=dtype)
            n = X.shape[0]
            Z = torch.randn(n, m, device=device, dtype=dtype)
            Z.sub_(Z.mean(dim=0, keepdim=True))
            numer = torch.linalg.norm(X.T @ Z, ord=float("inf"), dim=0)
            denom = torch.linalg.norm(Z, ord=2, dim=0)
            lambdas = (numer / denom).to(torch.float32)
            return torch.quantile(lambdas, 0.95).item()

        # Multi-GPU case
        num_devices = torch.cuda.device_count()
        n = self.X.shape[0]

        # Compute how m is split across GPUs
        base = 0.7
        weights = [base**i for i in range(num_devices)]
        weight_sum = sum(weights)
        raw_splits = [(w / weight_sum) * m for w in weights]
        m_splits = [int(round(val)) for val in raw_splits]
        diff = m - sum(m_splits)
        m_splits[0] += diff

        comp_streams = [torch.cuda.Stream(device=i) for i in range(num_devices)]
        lambdas: List[torch.Tensor] = [None] * num_devices

        for i, m_i in enumerate(m_splits):
            if m_i == 0:
                continue
            dev = f"cuda:{i}"
            X_dev = self._get_converted_X(device=dev, dtype=dtype)

            with torch.cuda.stream(comp_streams[i]):
                Z = torch.randn(n, m_i, device=dev, dtype=dtype)
                Z -= Z.mean(dim=0, keepdim=True)
                numer: torch.Tensor = torch.linalg.norm(
                    X_dev.T @ Z, ord=float("inf"), dim=0
                )
                denom: torch.Tensor = torch.linalg.norm(Z, ord=2, dim=0)
                lambdas[i] = (numer / denom).to(
                    device="cuda:0", dtype=torch.float32, non_blocking=True
                )

        for s in comp_streams:
            s.synchronize()

        return torch.quantile(torch.cat(lambdas, dim=0), 0.95).item()
