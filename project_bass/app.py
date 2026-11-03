import tempfile
from pathlib import Path

import numpy as np
import pyvista as pv
import streamlit as st
import trimesh

from crypto_engine import decrypt_mesh, encrypt_mesh
from data_loader import load_mesh

st.set_page_config(page_title="3D Mesh Encryption System", layout="wide")

st.title("3D Mesh Encryption System")

with st.sidebar:
    st.header("Secret Keys")
    x0 = st.number_input("x0", value=0.456789, min_value=0.0, max_value=1.0, step=0.000001, format="%.6f")
    r = st.number_input("r", value=3.9999, min_value=0.0, max_value=10.0, step=0.0001, format="%.4f")

st.subheader("System Overview")

col1, col2 = st.columns(2)
with col1:
    st.info("Mesh encryption workflow is ready for configuration.")
with col2:
    st.success(f"Active keys: x0 = {x0}, r = {r}")

st.markdown("---")

st.subheader("Upload 3D Mesh")
uploaded_file = st.file_uploader(
    "Choose a .ply or .obj mesh file",
    type=["ply", "obj"],
    help="Upload a mesh file to be saved temporarily for Trimesh processing.",
)

mesh = None
temp_mesh_path = None
if uploaded_file is not None:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in {".ply", ".obj"}:
        st.error("Unsupported file type. Please upload a .ply or .obj file.")
    else:
        temp_dir = tempfile.mkdtemp(prefix="mesh_")
        temp_mesh_path = Path(temp_dir) / uploaded_file.name
        temp_mesh_path.write_bytes(uploaded_file.getvalue())
        st.session_state["mesh_path"] = str(temp_mesh_path)
        st.success(f"Temporary file saved: {temp_mesh_path}")

        try:
            mesh = load_mesh(temp_mesh_path)
            vertex_count = len(mesh.vertices)
            face_count = len(mesh.faces)
            st.session_state["mesh"] = mesh
            st.info(f"Trimesh loaded the mesh successfully with {vertex_count} vertices and {face_count} faces.")
        except Exception as exc:
            st.warning(f"File saved, but Trimesh could not load it: {exc}")

st.markdown("---")

col_encrypt, col_decrypt = st.columns(2)
with col_encrypt:
    encrypt_clicked = st.button("Encrypt")
with col_decrypt:
    decrypt_clicked = st.button("Decrypt")

if encrypt_clicked:
    if mesh is None:
        st.warning("Please upload a mesh before encrypting.")
    else:
        encrypted_vertices = encrypt_mesh(mesh, x0=x0, r=r)
        st.session_state["encrypted_vertices"] = encrypted_vertices
        st.success("Mesh encrypted successfully and stored in session state.")

if decrypt_clicked:
    if "encrypted_vertices" not in st.session_state:
        st.warning("No encrypted mesh is available in session state to decrypt.")
    else:
        decrypted_vertices = decrypt_mesh(st.session_state["encrypted_vertices"], x0=x0, r=r)
        st.session_state["decrypted_vertices"] = decrypted_vertices
        st.success("Mesh decrypted successfully and stored in session state.")

st.markdown("---")

original_mesh = mesh
processed_vertices = None
if "encrypted_vertices" in st.session_state:
    processed_vertices = st.session_state["encrypted_vertices"]
elif "decrypted_vertices" in st.session_state:
    processed_vertices = st.session_state["decrypted_vertices"]

if original_mesh is not None:
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("Original")
        original_pv = pv.PolyData(original_mesh.vertices, original_mesh.faces.reshape(-1, 4))
        original_plot = pv.Plotter(window_size=[500, 400])
        original_plot.add_mesh(original_pv, color="lightblue", show_edges=True, smooth_shading=True)
        original_plot.camera_position = [(3, 3, 3), (0, 0, 0), (0, 1, 0)]
        original_plot.background_color = "white"
        st.pyplot(original_plot)

    with right_col:
        st.subheader("Processed")
        if processed_vertices is not None:
            processed_mesh = trimesh.Trimesh(vertices=processed_vertices, faces=original_mesh.faces, process=False)
            processed_pv = pv.PolyData(processed_mesh.vertices, processed_mesh.faces.reshape(-1, 4))
            processed_plot = pv.Plotter(window_size=[500, 400])
            processed_plot.add_mesh(processed_pv, color="tomato", show_edges=True, smooth_shading=True)
            processed_plot.camera_position = [(3, 3, 3), (0, 0, 0), (0, 1, 0)]
            processed_plot.background_color = "white"
            st.pyplot(processed_plot)
        else:
            st.info("Encrypt or decrypt a mesh to view the processed result.")

    if processed_vertices is not None:
        processed_obj = trimesh.Trimesh(vertices=processed_vertices, faces=original_mesh.faces, process=False)
        obj_data = processed_obj.export(file_type="obj")
        st.download_button(
            label="Download processed .obj",
            data=obj_data,
            file_name="processed_mesh.obj",
            mime="text/plain",
        )
else:
    st.info("Upload a mesh to start encryption and visualization.")
