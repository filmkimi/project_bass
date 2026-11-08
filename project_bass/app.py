import tempfile
import time
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
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
    "Choose a 3D mesh file (.ply, .obj, .stl, .off, .glb, .gltf)",
    type=["ply", "obj", "stl", "off", "glb", "gltf"],
    help="Upload a mesh file to be saved temporarily for Trimesh processing.",
)

vertices, faces = None, None

if uploaded_file is not None:
    suffix = Path(uploaded_file.name).suffix.lower()
    allowed_suffixes = {".ply", ".obj", ".stl", ".off", ".glb", ".gltf"}
    
    if suffix not in allowed_suffixes:
        st.error(f"Unsupported file type. Allowed: {', '.join(allowed_suffixes)}")
    else:
        temp_dir = tempfile.mkdtemp(prefix="mesh_")
        temp_mesh_path = Path(temp_dir) / uploaded_file.name
        temp_mesh_path.write_bytes(uploaded_file.getvalue())
        st.session_state["mesh_path"] = str(temp_mesh_path)

        try:
            vertices, faces = load_mesh(temp_mesh_path)
            st.session_state["vertices"] = vertices
            st.session_state["faces"] = faces
            st.info(f"Loaded mesh successfully: {len(vertices)} vertices, {len(faces)} faces.")
        except Exception as exc:
            st.warning(f"File saved, but Trimesh could not load it: {exc}")

st.markdown("---")

col_encrypt, col_decrypt = st.columns(2)
with col_encrypt:
    encrypt_clicked = st.button("Encrypt")
with col_decrypt:
    decrypt_clicked = st.button("Decrypt")

if "vertices" in st.session_state and "faces" in st.session_state:
    vertices = st.session_state["vertices"]
    faces = st.session_state["faces"]

if encrypt_clicked:
    if vertices is None:
        st.warning("Please upload a mesh before encrypting.")
    else:
        start_time = time.time()
        encrypted_vertices, perm_indices = encrypt_mesh(vertices, x0=x0, r=r)
        end_time = time.time()
        
        enc_duration = end_time - start_time
        st.session_state["enc_time"] = enc_duration
        st.session_state["encrypted_vertices"] = encrypted_vertices
        st.session_state["perm_indices"] = perm_indices
        
        if "decrypted_vertices" in st.session_state:
            del st.session_state["decrypted_vertices"]
            
        st.success(f"Mesh encrypted successfully in {enc_duration:.4f} seconds!")

if decrypt_clicked:
    if "encrypted_vertices" not in st.session_state or "perm_indices" not in st.session_state:
        st.warning("No encrypted mesh is available to decrypt.")
    else:
        start_time = time.time()
        decrypted_vertices = decrypt_mesh(
            st.session_state["encrypted_vertices"],
            st.session_state["perm_indices"],
            x0=x0,
            r=r
        )
        end_time = time.time()
        
        dec_duration = end_time - start_time
        st.session_state["dec_time"] = dec_duration
        st.session_state["decrypted_vertices"] = decrypted_vertices
        
        st.success(f"Mesh decrypted successfully in {dec_duration:.4f} seconds!")

# ส่วนแสดงเวลาประมวลผล (Performance Metrics)
if "enc_time" in st.session_state or "dec_time" in st.session_state:
    st.markdown("### ⏱️ Performance Metrics")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        if "enc_time" in st.session_state:
            st.metric(label="Encryption Time", value=f"{st.session_state['enc_time']:.4f} s")
    with m_col2:
        if "dec_time" in st.session_state:
            st.metric(label="Decryption Time", value=f"{st.session_state['dec_time']:.4f} s")

st.markdown("---")

# ฟังก์ชันเรนเดอร์ 3D แบบหมุนได้ 360 องศาด้วย Plotly
def plot_mesh_3d_interactive(verts, faces_data, color="#00d2ff"):
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
    i, j, k = faces_data[:, 0], faces_data[:, 1], faces_data[:, 2]

    fig = go.Figure(data=[
        go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=color,
            opacity=0.8,
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.2), # เพิ่มแสงเงาให้มีมิติ
        )
    ])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data"
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=500
    )
    return fig

processed_vertices = None
if "decrypted_vertices" in st.session_state:
    processed_vertices = st.session_state["decrypted_vertices"]
elif "encrypted_vertices" in st.session_state:
    processed_vertices = st.session_state["encrypted_vertices"]

if vertices is not None and faces is not None:
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("Original Mesh (Interactive 3D)")
        fig_orig = plot_mesh_3d_interactive(vertices, faces, color="#00d2ff")
        st.plotly_chart(fig_orig, use_container_width=True)

    with right_col:
        st.subheader("Processed Mesh (Interactive 3D)")
        if processed_vertices is not None:
            fig_proc = plot_mesh_3d_interactive(processed_vertices, faces, color="#ff4b4b")
            st.plotly_chart(fig_proc, use_container_width=True)
        else:
            st.info("Click Encrypt or Decrypt to process mesh.")

    if processed_vertices is not None:
        processed_obj = trimesh.Trimesh(vertices=processed_vertices, faces=faces, process=False)
        obj_data = processed_obj.export(file_type="obj")
        st.download_button(
            label="Download processed .obj",
            data=obj_data,
            file_name="processed_mesh.obj",
            mime="text/plain",
        )
else:
    st.info("Upload a mesh to start encryption and visualization.")