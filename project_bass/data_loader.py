from pathlib import Path

import numpy as np
import trimesh


def normalize_vertices(
    vertices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Scale each vertex coordinate to [-1, 1], returning the original min and max."""
    vertices = np.asarray(vertices, dtype=float)
    if vertices.ndim != 2 or vertices.shape[0] == 0 or vertices.shape[1] == 0:
        raise ValueError("vertices must be a non-empty 2D array")
    if not np.isfinite(vertices).all():
        raise ValueError("vertices must contain only finite values")

    minimum = vertices.min(axis=0)
    maximum = vertices.max(axis=0)
    value_range = maximum - minimum
    normalized = np.zeros_like(vertices)
    np.divide(
        2 * (vertices - minimum),
        value_range,
        out=normalized,
        where=value_range != 0,
    )
    normalized = np.where(value_range != 0, normalized - 1, 0)
    return normalized, minimum, maximum


def denormalize_vertices(
    vertices: np.ndarray, minimum: np.ndarray, maximum: np.ndarray
) -> np.ndarray:
    """Restore vertices using the min and max returned by normalize_vertices."""
    vertices = np.asarray(vertices, dtype=float)
    minimum = np.asarray(minimum, dtype=float)
    maximum = np.asarray(maximum, dtype=float)
    if vertices.ndim != 2 or minimum.ndim != 1 or maximum.ndim != 1:
        raise ValueError("vertices must be 2D and minimum/maximum must be 1D")
    if vertices.shape[1] != minimum.size or minimum.shape != maximum.shape:
        raise ValueError("vertices and min/max dimensions must match")
    if (
        not np.isfinite(vertices).all()
        or not np.isfinite(minimum).all()
        or not np.isfinite(maximum).all()
    ):
        raise ValueError("vertices and min/max must contain only finite values")
    if np.any(maximum < minimum):
        raise ValueError("maximum must be greater than or equal to minimum")

    return (vertices + 1) * (maximum - minimum) / 2 + minimum


def reconstruct_mesh(
    vertices: np.ndarray,
    faces: np.ndarray,
    output_path: str | Path,
) -> Path:
    """Rebuild a mesh from its vertices and faces, and export it as an OBJ file."""
    vertices = np.asarray(vertices, dtype=float)
    faces = np.asarray(faces)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or vertices.shape[0] == 0:
        raise ValueError("vertices must be a non-empty Nx3 array")
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("faces must be an Nx3 array of triangle indices")
    if not np.isfinite(vertices).all():
        raise ValueError("vertices must contain only finite values")
    if not np.issubdtype(faces.dtype, np.integer):
        raise ValueError("face indices must be integers")
    if faces.size and (np.any(faces < 0) or np.any(faces >= len(vertices))):
        raise ValueError("face indices must refer to existing vertices")

    path = Path(output_path)
    if path.suffix.lower() != ".obj":
        raise ValueError("output_path must have an .obj extension")

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.export(path, file_type="obj")
    return path


def load_mesh(mesh_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load a PLY or OBJ mesh and return its vertices and faces."""
    path = Path(mesh_path)
    if path.suffix.lower() not in {".ply", ".obj"}:
        raise ValueError(f"Unsupported mesh file type: {path.suffix}")

    mesh = trimesh.load(path, force="mesh")
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"File does not contain a 3D mesh: {path}")

    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    return vertices, faces
