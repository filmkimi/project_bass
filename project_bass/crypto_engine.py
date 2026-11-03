import numpy as np


def generate_logistic_map(x0: float, r: float, length: int) -> np.ndarray:
    """Generate ``length`` logistic-map values, starting with ``x0``."""
    values = np.empty(length, dtype=float)
    if length == 0:
        return values

    values[0] = x0
    for index in range(1, length):
        values[index] = r * values[index - 1] * (1 - values[index - 1])

    return values


def encrypt_mesh(
    vertices: np.ndarray, x0: float, r: float
) -> tuple[np.ndarray, np.ndarray]:
    """Permute mesh vertices and add a logistic-map mask to each coordinate."""
    vertices = np.asarray(vertices, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("vertices must have shape (N, 3)")

    vertex_count = len(vertices)
    perm_sequence = generate_logistic_map(x0, r, vertex_count)
    perm_indices = np.argsort(perm_sequence)

    mask_sequence = generate_logistic_map(x0, r, vertex_count * 3)
    coordinate_mask = mask_sequence.reshape(vertex_count, 3)
    encrypted_vertices = vertices[perm_indices] + coordinate_mask

    return encrypted_vertices, perm_indices


def decrypt_mesh(
    encrypted_vertices: np.ndarray,
    perm_indices: np.ndarray,
    x0: float,
    r: float,
) -> np.ndarray:
    """Remove the logistic-map mask and restore the original vertex order."""
    encrypted_vertices = np.asarray(encrypted_vertices, dtype=float)
    perm_indices = np.asarray(perm_indices)
    if encrypted_vertices.ndim != 2 or encrypted_vertices.shape[1] != 3:
        raise ValueError("encrypted_vertices must have shape (N, 3)")
    if perm_indices.ndim != 1 or len(perm_indices) != len(encrypted_vertices):
        raise ValueError("perm_indices must have shape (N,)")

    vertex_count = len(encrypted_vertices)
    mask_sequence = generate_logistic_map(x0, r, vertex_count * 3)
    coordinate_mask = mask_sequence.reshape(vertex_count, 3)
    permuted_vertices = encrypted_vertices - coordinate_mask
    inverse_permutation = np.argsort(perm_indices)
    decrypted_vertices = permuted_vertices[inverse_permutation]

    return decrypted_vertices