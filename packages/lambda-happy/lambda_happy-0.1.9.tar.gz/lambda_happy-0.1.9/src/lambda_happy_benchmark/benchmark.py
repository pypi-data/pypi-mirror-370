import time
from datetime import datetime
from typing import Callable, Optional

import torch
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from lambda_happy import LambdaHappy
from .lambda_happy_partial import LambdaHappyPartial


class LambdaBenchmark:
    """Benchmark utility for evaluating LambdaHappy performance."""

    def __init__(self, estimator: LambdaHappy):
        """Initializes with estimator"""
        self.estimator = estimator
        self.tested_versions = ["SMART_TENSOR", "GPU_DEDICATED"]
        self.dtype_map = {torch.float32: "f32", torch.float16: "f16"}

        self.USE_AGG = matplotlib.get_backend().lower() == "agg"

    def _sync(self):
        """Synchronizes CUDA if available."""
        if self.estimator.get_device_type() == "cuda" and torch.cuda.is_available():
            torch.cuda.synchronize()

    def _benchmark_single(
        self,
        m: int = 100_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        """Benchmarks compute throughput (FPS) for given config.

        Args:
            m (int, optional): Number of samples. Defaults to 100_000.
            version (str, optional): Version to test. Defaults to "AUTOMATIC".
            device_type (Optional[str], optional): Target device. Defaults to None.
            dtype (Optional[torch.dtype], optional): Data type. Defaults to None.

        Returns:
            float: Frames per second (FPS).
        """
        _ = self.estimator.compute(
            m=1_000, version=version, device_type=device_type, dtype=dtype
        )
        self._sync()
        start = time.perf_counter()
        _ = self.estimator.compute(
            m=m, version=version, device_type=device_type, dtype=dtype
        )
        self._sync()
        return 1.0 / (time.perf_counter() - start)

    def _benchmark_many(
        self,
        nb_run: int = 20,
        m: int = 10_000,
        version: str = "AUTOMATIC",
        device_type: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> float:
        """Benchmarks compute_many throughput over multiple runs.

        Args:
            nb_run (int): Number of executions.
            m (int): Number of samples per run.
            version (str): Estimator version.
            device_type (Optional[str]): Device to run on ("cpu" or "cuda").
            dtype (Optional[torch.dtype]): Data type to use.

        Returns:
            float: Frames per second (FPS).
        """
        [
            self.estimator.compute(
                m=m, version=version, device_type=device_type, dtype=dtype
            )
            for _ in range(10)
        ]
        self._sync()
        start = time.perf_counter()
        _ = self.estimator.compute_many(
            nb_run, m=m, version=version, device_type=device_type, dtype=dtype
        )
        self._sync()
        return nb_run / (time.perf_counter() - start)

    def _benchmark_many_callable(
        self, nb_run: int, target_callable: Callable[[], Optional[float]]
    ) -> float:
        """Benchmarks a callable over multiple runs.

        Args:
            nb_run (int): Number of executions.
            target_callable (Callable): Callable to benchmark.

        Returns:
            float: Executions per second (FPS).
        """
        target_callable()
        self._sync()

        start = time.perf_counter()
        for _ in range(nb_run):
            target_callable()
        self._sync()
        elapsed = time.perf_counter() - start
        return nb_run / elapsed

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
            plt.close(fig)
        else:
            plt.show(block=True)
            plt.pause(0.1)

    def show_benchmark_2D(
        self,
        m_values: np.ndarray = None,
        p_values: np.ndarray = None,
        n: int = 1_000,
        p: int = 1_000,
        m: int = 10_000,
        version: str = "AUTOMATIC",
    ) -> None:
        """Runs and plots 2D benchmarks varying m and p.

        Args:
            m_values (np.ndarray, optional): Values of m to test.
            p_values (np.ndarray, optional): Values of p to test.
            n (int): Fixed number of rows.
            p (int): Default number of columns.
            m (int): Default number of samples.
            version (str): Estimator version.
        """

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        if p_values is None:
            p_values = 10 * 2 ** np.arange(11)

        original_estimator = self.estimator

        benchmark_m_results = {"pytorch_cpu": [], "pytorch_cuda": []}
        benchmark_nb_cols_results = {"pytorch_cpu": [], "pytorch_cuda": []}
        for m_value in m_values:
            X = torch.randn(
                n,
                p,
                dtype=original_estimator.get_dtype(),
            )
            self.estimator = LambdaHappy(X)
            benchmark_m_results["pytorch_cpu"].append(
                self._benchmark_many(m=m_value, version=version, device_type="cpu")
            )
            benchmark_m_results["pytorch_cuda"].append(
                self._benchmark_many(m=m_value, version=version, device_type="cuda")
            )

        for p_value in p_values:
            X = torch.randn(
                n,
                p_value,
                device=original_estimator.get_device_type(),
                dtype=original_estimator.get_dtype(),
            )
            self.estimator = LambdaHappy(X)
            benchmark_nb_cols_results["pytorch_cpu"].append(
                self._benchmark_many(m=m, version=version, device_type="cpu")
            )
            benchmark_nb_cols_results["pytorch_cuda"].append(
                self._benchmark_many(m=m, version=version, device_type="cuda")
            )

        self.estimator = original_estimator
        dtype_str = self.dtype_map.get(original_estimator.get_dtype())

        m_max = m_values[-1]
        fps_cpu_max_m = benchmark_m_results["pytorch_cpu"][-1]
        fps_cuda_max_m = benchmark_m_results["pytorch_cuda"][-1]

        fig, axs = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(
            f"Benchmark 2D: Variation of m\n"
            f"(n={n}, p={p}, version={version}, dtype={dtype_str})",
            fontsize=14,
        )

        # FPS plot
        axs[0].plot(
            m_values,
            benchmark_m_results["pytorch_cpu"],
            label=f"CPU (m={m_max} : {fps_cpu_max_m:.0f} FPS)",
            color="blue",
        )
        axs[0].plot(
            m_values,
            benchmark_m_results["pytorch_cuda"],
            label=f"CUDA (m={m_max} : {fps_cuda_max_m:.0f} FPS)",
            color="red",
        )
        axs[0].set_title("FPS Comparison")
        axs[0].set_xlabel("m Size")
        axs[0].set_ylabel("FPS (s$^{-1}$)")
        axs[0].legend()
        axs[0].grid(True)

        # Speed-up plot
        speed_up_m = np.array(benchmark_m_results["pytorch_cuda"]) / np.array(
            benchmark_m_results["pytorch_cpu"]
        )
        axs[1].plot(m_values, speed_up_m, label="Speed Up (CUDA / CPU)", color="black")
        axs[1].set_title("Speed Up: CUDA over CPU")
        axs[1].set_xlabel("m Size")
        axs[1].set_ylabel("Speed Up")
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        self._finalize_plot(
            fig,
            name="benchmark_2D_m",
            params={"version": version},
            dtype=dtype_str,
        )

        p_max = p_values[-1]
        fps_cpu_max_p = benchmark_nb_cols_results["pytorch_cpu"][-1]
        fps_cuda_max_p = benchmark_nb_cols_results["pytorch_cuda"][-1]

        fig, axs = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(
            f"Benchmark 2D: Variation of p\n"
            f"(n={n}, m={m}, version={version}, dtype={dtype_str})",
            fontsize=14,
        )

        # FPS plot
        axs[0].plot(
            p_values,
            benchmark_nb_cols_results["pytorch_cpu"],
            label=f"CPU (p={p_max} : {fps_cpu_max_p:.0f} FPS)",
            color="blue",
        )
        axs[0].plot(
            p_values,
            benchmark_nb_cols_results["pytorch_cuda"],
            label=f"CUDA (p={p_max} : {fps_cuda_max_p:.0f} FPS)",
            color="red",
        )
        axs[0].set_title("FPS Comparison")
        axs[0].set_xlabel("p Size")
        axs[0].set_ylabel("FPS (s$^{-1}$)")
        axs[0].legend()
        axs[0].grid(True)

        # Speed-up plot
        speed_up_p = np.array(benchmark_nb_cols_results["pytorch_cuda"]) / np.array(
            benchmark_nb_cols_results["pytorch_cpu"]
        )
        axs[1].plot(p_values, speed_up_p, label="Speed Up (CUDA / CPU)", color="black")
        axs[1].set_title("Speed Up:CUDA over CPU")
        axs[1].set_xlabel("p Size")
        axs[1].set_ylabel("Speed Up")
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        self._finalize_plot(
            fig,
            name="benchmark_2D_p",
            params={"version": version},
            dtype=dtype_str,
        )

    def show_benchmark_3D(
        self,
        m_values: np.ndarray = None,
        p_values: np.ndarray = None,
        n: int = 1_000,
        version: str = "AUTOMATIC",
    ) -> None:
        """Runs and plots 3D benchmark with varying m and p.

        Args:
            m_values (np.ndarray, optional): Values of m to test.
            p_values (np.ndarray, optional): Values of p to test.
            n (int): Fixed number of rows.
            version (str): Estimator version.
        """

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        if p_values is None:
            p_values = 10 * 2 ** np.arange(11)

        original_estimator = self.estimator
        original_estimator_dtype = self.estimator.get_dtype()
        benchmark_results = {
            "pytorch_cpu": np.zeros((len(m_values), len(p_values))),
            "pytorch_cuda": np.zeros((len(m_values), len(p_values))),
        }

        for i, m in enumerate(m_values):
            for j, p in enumerate(p_values):
                X = torch.randn(n, p, dtype=original_estimator_dtype)
                self.estimator = LambdaHappy(X)
                benchmark_results["pytorch_cpu"][i, j] = self._benchmark_many(
                    m=m, version=version, device_type="cpu"
                )

                if torch.cuda.is_available():
                    benchmark_results["pytorch_cuda"][i, j] = self._benchmark_many(
                        m=m, version=version, device_type="cuda"
                    )

        self.estimator = original_estimator

        M, P = np.meshgrid(m_values, p_values, indexing="ij")

        fig = plt.figure(figsize=(14, 6))
        fig.suptitle(
            f"Benchmark 3D : Variation of m and p\n"
            f"(n={n}, version={version}, dtype={self.dtype_map.get(original_estimator_dtype)})",
            fontsize=14,
        )
        # 3D plot CPU
        ax1 = fig.add_subplot(121, projection="3d")
        ax1.plot_surface(M, P, benchmark_results["pytorch_cpu"], cmap="Blues")
        ax1.set_title(f"CPU")
        ax1.set_xlabel("m Size")
        ax1.set_ylabel("p Size")
        ax1.set_zlabel("FPS (s$^{-1}$)")

        # 3D plot CUDA
        ax2 = fig.add_subplot(122, projection="3d")
        ax2.plot_surface(M, P, benchmark_results["pytorch_cuda"], cmap="Reds")
        ax2.set_title(f"CUDA")
        ax2.set_xlabel("m Size")
        ax2.set_ylabel("p Size")
        ax2.set_zlabel("FPS (s$^{-1}$)")

        plt.tight_layout()

        self._finalize_plot(
            fig,
            name="benchmark_3D",
            params={
                "version": version,
            },
            dtype=self.dtype_map.get(original_estimator.get_dtype()),
        )

    def show_benchmark_float(
        self, m_values: np.ndarray = None, version: str = "SMART_TENSOR", nb_run=500
    ) -> None:
        """Compares performance between float16 and float32.

        Args:
            m_values (np.ndarray, optional): m values to test. Defaults to range.
            version (str): Estimator version. Defaults to "SMART_TENSOR".
            nb_run (int): Number of runs per m. Defaults to 500.
        """

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        benchmark_m_results = {"float16": [], "float32": []}

        for m in m_values:
            benchmark_m_results["float16"].append(
                self._benchmark_many(
                    m=m,
                    nb_run=nb_run,
                    version=version,
                    dtype=torch.float16,
                )
            )
            benchmark_m_results["float32"].append(
                self._benchmark_many(
                    m=m,
                    nb_run=nb_run,
                    version=version,
                    dtype=torch.float32,
                )
            )

        m_max = m_values[-1]
        fps_f16_max = benchmark_m_results["float16"][-1]
        fps_f32_max = benchmark_m_results["float32"][-1]

        fig, axs = plt.subplots(1, 2, figsize=(14, 6))

        n, p = self.estimator.X.shape
        fig.suptitle(
            "Benchmark: float16 vs float32\n"
            f"({n=}, {p=}, version={version}, device={self.estimator.get_device_type()})",
            fontsize=14,
        )

        axs[0].plot(
            m_values,
            benchmark_m_results["float16"],
            label=f"float16 (m={m_max} : {fps_f16_max:.0f} FPS)",
            color="b",
        )
        axs[0].plot(
            m_values,
            benchmark_m_results["float32"],
            label=f"float32 (m={m_max} : {fps_f32_max:.0f} FPS)",
            color="r",
        )
        axs[0].set_title("FPS Comparison")
        axs[0].set_xlabel("m Size")
        axs[0].set_ylabel("FPS (s$^{-1}$)")
        axs[0].legend()
        axs[0].grid(True)

        # Speed Up = float16 / float32
        fps_f16 = np.array(benchmark_m_results["float16"])
        fps_f32 = np.array(benchmark_m_results["float32"])
        gain_factor = fps_f16 / fps_f32

        axs[1].plot(m_values, gain_factor, label="Speed Up", color="black")
        axs[1].set_title("Speed Up: float16 over float32")
        axs[1].set_xlabel("m Size")
        axs[1].set_ylabel("Speed Up (float16 / float32)")
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        self._finalize_plot(
            fig,
            name="benchmark_float",
            params={
                "version": version,
            },
            device=self.estimator.get_device_type(),
        )

    def show_benchmark_version(self, m_values: np.ndarray = None) -> None:
        """Compares performance between estimator versions over m.

        Args:
            m_values (np.ndarray, optional): m values to test. Defaults to range.
        """

        if m_values is None:
            m_values = 10 * 2 ** np.arange(11)

        benchmark_m = {v: [] for v in self.tested_versions}

        # Benchmark with different m
        for m in m_values:
            for version in self.tested_versions:
                fps = self._benchmark_many(version=version, device_type="cuda", m=m)
                benchmark_m[version].append(fps)

        # Benchmark with different p
        original_estimator = self.estimator
        original_type = original_estimator.get_dtype()

        self.estimator = original_estimator

        # Plot variation de m
        fig, axs = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(
            f"GPU Benchmark ({self.tested_versions[0]} vs {self.tested_versions[1]})\n"
            f"Variation of m (dtype={self.dtype_map.get(original_type)})",
            fontsize=14,
        )
        m_max = m_values[-1]
        for version in self.tested_versions:
            fps_max = benchmark_m[version][-1]
            axs[0].plot(
                m_values,
                benchmark_m[version],
                label=f"{version} (m={m_max} : {fps_max:.0f} FPS)",
            )

        axs[0].set_title("FPS Comparison")
        axs[0].set_xlabel("m Size")
        axs[0].set_ylabel("FPS (s$^{-1}$)")
        axs[0].legend()
        axs[0].grid(True)

        fps_1 = np.array(benchmark_m[self.tested_versions[0]])
        fps_2 = np.array(benchmark_m[self.tested_versions[1]])
        speed_up = fps_2 / fps_1

        axs[1].plot(m_values, speed_up, label="Speed Up", color="black")
        axs[1].set_title(
            f"Speed Up: {self.tested_versions[1]} over {self.tested_versions[0]}"
        )
        axs[1].set_xlabel("m Size")
        axs[1].set_ylabel("Speed Up")
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        self._finalize_plot(
            fig,
            name="benchmark_version_m_variation",
            device="cuda",
            dtype=self.dtype_map.get(original_type),
        )

    def benchmark_partial(
        self, n: int = 1_000, p: int = 1_000, m: int = 10_000, nb_run: int = 500
    ) -> None:
        """Benchmarks each step of LambdaHappyPartial pipeline.

        Args:
            n (int): Number of rows. Defaults to 1_000.
            p (int): Number of columns. Defaults to 1_000.
            m (int): Number of samples. Defaults to 10_000.
            nb_run (int): Number of repetitions per step. Defaults to 500.
        """

        original_estimator = self.estimator
        device_type = original_estimator.get_device_type()
        dtype = original_estimator.get_dtype()
        X = torch.randn(n, p, device=device_type, dtype=dtype)

        partial_estimator = LambdaHappyPartial(
            X, m, device_type=device_type, dtype=dtype
        )
        self.estimator = LambdaHappy(X)

        total_time = 0.0

        for target_callable in partial_estimator.pipeline:
            partial_estimator.prepare_func(target_callable)
            mean_fps = self._benchmark_many_callable(nb_run, lambda: target_callable())
            print(
                f"Mean FPS over {nb_run} runs of {target_callable.__func__.__name__:31s} : {mean_fps:.8f} FPS ({(1/mean_fps):.8f} sec)"
            )
            if target_callable not in (
                partial_estimator.chain1,
                partial_estimator.chain2,
            ):
                total_time += 1 / mean_fps

        for version in self.tested_versions:
            mean_fps = self._benchmark_many(
                nb_run=nb_run,
                m=m,
                version=version,
                device_type=device_type,
                dtype=dtype,
            )
            print(
                f"Mean FPS over {nb_run} runs of {self.estimator.__class__.__name__:31s} : {mean_fps:.8f} FPS ({(1/mean_fps):.8f} sec) (version={version})"
            )
        self.estimator = original_estimator

        fps_theorical = 1.0 / total_time if total_time > 0 else float("inf")
        print(
            f"Theorical LambdaHappy mean FPS (sum of independent steps) : {fps_theorical:.8f} FPS ({total_time:.8f} sec) (version=SMART_TENSOR)"
        )

    def show_benchmark_format_conversion(
        self, n: int = 1_000, p: int = 1_000, m=10_000
    ):
        """Evaluates performance impact of format conversion (device/dtype).

        Args:
            n (int): Number of rows. Defaults to 1_000.
            p (int): Number of columns. Defaults to 1_000.
            m (int): Number of samples. Defaults to 10_000.
        """
        original_estimator = self.estimator
        scenarios = [
            ("cpu_f32", "cpu", torch.float32),
            ("cpu_f16", "cpu", torch.float16),
            ("cuda_f32", "cuda", torch.float32),
            ("cuda_f16", "cuda", torch.float16),
        ]
        for init_name, init_dev, init_dtype in scenarios:
            dev = (
                init_dev
                if not (init_dev == "cuda" and not torch.cuda.is_available())
                else "cpu"
            )

            X = torch.randn(n, p, device=dev, dtype=init_dtype)
            self.estimator = LambdaHappy(X)
            single_fps = []
            many_fps = []
            version = "AUTOMATIC"
            for name, device, dtype in scenarios:
                single_fps.append(
                    self._benchmark_single(
                        m=m, version=version, device_type=device, dtype=dtype
                    )
                )
                many_fps.append(
                    self._benchmark_many(
                        nb_run=100,
                        m=m,
                        version=version,
                        device_type=device,
                        dtype=dtype,
                    )
                )
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.suptitle(
                f"Format Conversion Benchmark Initial Format: {init_name.replace('_', ' ').upper()}\n"
                f"(version={version})",  # CPU: only with pytorch, AUTOMATIC = FASTEST For each case
                fontsize=14,
                fontweight="bold",
            )
            x = np.arange(len(scenarios))
            width = 0.35
            ax.bar(x - width / 2, single_fps, width, label="single")
            ax.bar(x + width / 2, many_fps, width, label="many")
            ax.set_xticks(x)
            ax.set_xticklabels([name for name, _, _ in scenarios])
            ax.set_ylabel("FPS")
            ax.legend()
            plt.tight_layout()
            self._finalize_plot(
                fig,
                name=f"format_{init_name}",
            )
        self.estimator = original_estimator
