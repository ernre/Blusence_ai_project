"""Latency optimization package."""

from vpe.latency.benchmark import BenchmarkResult, run_benchmark
from vpe.latency.optimizer import LatencyOptimizationPlan, export_tensorrt_stub

__all__ = ["BenchmarkResult", "LatencyOptimizationPlan", "export_tensorrt_stub", "run_benchmark"]
