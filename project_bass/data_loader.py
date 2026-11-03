from __future__ import annotations

from pathlib import Path

import trimesh


def load_mesh(file_path):
    """Load a mesh from a .ply or .obj file path."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Mesh file not found: {path}")

    mesh = trimesh.load(str(path), force="scene")
    if mesh is None:
        raise ValueError(f"Could not load mesh from {path}")

    if isinstance(mesh, trimesh.Scene):
        if len(mesh.geometry) == 0:
            raise ValueError(f"Scene is empty for {path}")
        mesh = next(iter(mesh.geometry.values()))

    return mesh
