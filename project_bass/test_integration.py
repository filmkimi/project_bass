import numpy as np
import trimesh
import os
from data_loader import load_mesh
from crypto_engine import encrypt_mesh, decrypt_mesh
from evaluation import calculate_mse

def ensure_sample_file(filename):
    """ตรวจสอบว่ามีไฟล์ 3D หรือไม่ ถ้าไม่มีจะสร้างไฟล์จำลองให้ทันที"""
    if not os.path.exists(filename):
        print(f"-> ไม่พบไฟล์ '{filename}' ในโฟลเดอร์ กำลังสร้างไฟล์จำลอง...")
        mesh = trimesh.creation.box()
        mesh.export(filename)
        print(f"-> สร้างไฟล์ {filename} สำเร็จเรียบร้อย!\n")

def run_integration_test(mesh_path):
    print("=== ขั้นตอนที่ 1: โหลดไฟล์ 3D (Data Loader) ===")
    vertices, faces = load_mesh(mesh_path)
    print(f"-> โหลดไฟล์สำเร็จ! จำนวน Vertices: {len(vertices)}, จำนวน Faces: {len(faces)}")
    
    # กำหนดค่า Secret Key สำหรับทดสอบ
    x0_key = 0.456789
    r_key = 3.9999
    
    print("\n=== ขั้นตอนที่ 2: เข้ารหัส 3D Mesh (Crypto Engine) ===")
    encrypted_verts, perm_indices = encrypt_mesh(vertices, x0=x0_key, r=r_key)
    print("-> เข้ารหัสเสร็จสิ้น!")
    
    print("\n=== ขั้นตอนที่ 3: ถอดรหัส 3D Mesh (Crypto Engine) ===")
    decrypted_verts = decrypt_mesh(encrypted_verts, perm_indices, x0=x0_key, r=r_key)
    print("-> ถอดรหัสเสร็จสิ้น!")
    
    print("\n=== ขั้นตอนที่ 4: ตรวจสอบความถูกต้องสมบูรณ์ 100% (Lossless Test) ===")
    mse_score = calculate_mse(vertices, decrypted_verts)
    print(f"-> ค่า MSE (Mean Squared Error): {mse_score}")
    
    if np.isclose(mse_score, 0.0):
        print("✅ PASS: ถอดรหัสถูกต้อง ข้อมูลคืนค่าสมบูรณ์ 100% (Lossless)!")
    else:
        print("❌ FAIL: ข้อมูลหลังถอดรหัสไม่ตรงกับไฟล์ต้นฉบับ!")

    print("\n=== ขั้นตอนที่ 5: ทดสอบใส่ Key ผิด (Key Sensitivity Test) ===")
    wrong_x0 = 0.456788  # เปลี่ยนค่า x0 เล็กน้อยเพียง 0.000001
    wrong_decrypted = decrypt_mesh(encrypted_verts, perm_indices, x0=wrong_x0, r=r_key)
    wrong_mse = calculate_mse(vertices, wrong_decrypted)
    print(f"-> ค่า MSE เมื่อใส่ Key ผิด: {wrong_mse}")
    
    if wrong_mse > 0.1:
        print("✅ PASS: Key มีความไวสูงมาก เปลี่ยนค่าเพียงนิดเดียวจะไม่สามารถถอดรหัสได้!")

if __name__ == "__main__":
    sample_file = "cube.ply"
    
    # เช็กและสร้างไฟล์จำลองให้อัตโนมัติก่อนทดสอบ
    ensure_sample_file(sample_file)
    
    try:
        run_integration_test(sample_file)
    except Exception as e:
        print(f"\n⚠️ เกิดข้อผิดพลาดในการรัน: {e}")