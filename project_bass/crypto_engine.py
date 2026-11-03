from __future__ import annotations

import numpy as np


def _logistic_map(length: int, x0: float, r: float) -> np.ndarray:
    values = np.empty(length, dtype=float)
    values[0] = float(x0)
    for index in range(1, length):
        values[index] = float(r * values[index - 1] * (1.0 - values[index - 1]))
    return values


def encrypt_mesh(mesh, x0: float = 0.456789, r: float = 3.9999) -> np.ndarray:
    vertices = np.asarray(mesh.vertices, dtype=float)
    if vertices.size == 0:
        return vertices.copy()

    key_stream = _logistic_map(vertices.shape[0], x0, r)
    encrypted = vertices.copy()
    encrypted[:, 0] += key_stream
    encrypted[:, 1] -= key_stream * 0.5
    encrypted[:, 2] *= 1.0 + (key_stream * 0.01)
    return encrypted.astype(float)


def decrypt_mesh(encrypted_vertices, x0: float = 0.456789, r: float = 3.9999) -> np.ndarray:
    encrypted = np.asarray(encrypted_vertices, dtype=float)
    if encrypted.size == 0:
        return encrypted.copy()

    key_stream = _logistic_map(encrypted.shape[0], x0, r)
    decrypted = encrypted.copy()
    decrypted[:, 0] -= key_stream
    decrypted[:, 1] += key_stream * 0.5
    decrypted[:, 2] /= 1.0 + (key_stream * 0.01)
    return decrypted.astype(float)
