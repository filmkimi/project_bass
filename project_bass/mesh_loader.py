from pathlib import Path

import numpy as np
import trimesh


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
