from collections.abc import Callable
from time import perf_counter

import numpy as np
import matplotlib.pyplot as plt


def measure_execution_time(func: Callable[..., object], *args: object) -> float:
    """Return the average runtime in seconds over five calls to ``func``."""
    run_times = []
    for _ in range(5):
        start = perf_counter()
        func(*args)
        run_times.append(perf_counter() - start)

    return sum(run_times) / len(run_times)


def plot_vertex_histogram(
    original_verts: np.ndarray, encrypted_verts: np.ndarray
) -> None:
    """Compare original and encrypted vertex distributions along x, y, and z."""
    original = np.asarray(original_verts, dtype=np.float64)
    encrypted = np.asarray(encrypted_verts, dtype=np.float64)
    if (
        original.ndim != 2
        or encrypted.ndim != 2
        or original.shape[1] != 3
        or encrypted.shape[1] != 3
    ):
        raise ValueError("Vertex arrays must have shape (n, 3)")
    if original.shape[0] == 0 or encrypted.shape[0] == 0:
        raise ValueError("Vertex arrays must not be empty")

    figure, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    for index, coordinate in enumerate(("x", "y", "z")):
        bins = np.histogram_bin_edges(
            np.concatenate((original[:, index], encrypted[:, index])), bins=50
        )
        axes[index].hist(
            original[:, index], bins=bins, density=True, alpha=0.6, label="Original"
        )
        axes[index].hist(
            encrypted[:, index], bins=bins, density=True, alpha=0.6, label="Encrypted"
        )
        axes[index].set_title(f"{coordinate.upper()} coordinate")
        axes[index].set_xlabel("Coordinate value")
        axes[index].legend()

    axes[0].set_ylabel("Density")
    figure.tight_layout()
    plt.show()


def calculate_mse(
    original_verts: np.ndarray, decrypted_verts: np.ndarray
) -> float:
    """Calculate the mean squared error between two vertex arrays."""
    original = np.asarray(original_verts, dtype=np.float64)
    decrypted = np.asarray(decrypted_verts, dtype=np.float64)
    if original.shape != decrypted.shape:
        raise ValueError("Vertex arrays must have the same shape")
    if original.size == 0:
        raise ValueError("Vertex arrays must not be empty")

    return float(np.mean((original - decrypted) ** 2))