#!/usr/bin/env python3
"""GLB Model Diagnostic Tool - FIXED VERSION"""

import os
import sys

def test_with_trimesh():
    """Test loading with trimesh."""
    print("\n" + "="*60)
    print("TEST 1: Trimesh Loader")
    print("="*60)
    
    try:
        import trimesh
        
        models = [
            'assets/models/Anime_School_Teacher.GLB',
            'assets/models/old_female.glb'
        ]
        
        for model_path in models:
            if not os.path.exists(model_path):
                print(f"\n✗ File not found: {model_path}")
                continue
            
            print(f"\nLoading: {model_path}")
            print(f"File size: {os.path.getsize(model_path):,} bytes")
            
            try:
                scene = trimesh.load(model_path)
                
                if isinstance(scene, trimesh.Scene):
                    print(f"  ✓ Loaded as scene with {len(scene.geometry)} meshes")
                    
                    total_vertices = 0
                    total_faces = 0
                    
                    for name, mesh in scene.geometry.items():
                        if hasattr(mesh, 'vertices'):
                            verts = len(mesh.vertices)
                            faces = len(mesh.faces)
                            total_vertices += verts
                            total_faces += faces
                            print(f"    - {name}: {verts:,} verts, {faces:,} faces")
                    
                    print(f"  Total vertices: {total_vertices:,}")
                    print(f"  Total faces: {total_faces:,}")
                    
                    if total_vertices == 0:
                        print("  ✗ ERROR: No vertices - INVALID MODEL")
                        return False
                    else:
                        print("  ✓ Model has valid geometry")
                    
                    bounds = scene.bounds
                    if bounds is not None and len(bounds) == 2:
                        min_pt = bounds[0]
                        max_pt = bounds[1]
                        size = max_pt - min_pt
                        print(f"  Bounds min: [{min_pt[0]:.2f}, {min_pt[1]:.2f}, {min_pt[2]:.2f}]")
                        print(f"  Bounds max: [{max_pt[0]:.2f}, {max_pt[1]:.2f}, {max_pt[2]:.2f}]")
                        print(f"  Size: [{size[0]:.2f}, {size[1]:.2f}, {size[2]:.2f}]")
                        
                        if max(size) > 1000:
                            print(f"  ⚠ WARNING: Model is HUGE ({max(size):.2f})")
                        elif max(size) < 0.01:
                            print(f"  ⚠ WARNING: Model is TINY ({max(size):.6f})")
                        else:
                            print(f"  ✓ Size is reasonable")
                
                return True
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                return False
        
        return True
        
    except ImportError:
        print("✗ Trimesh not installed")
        print("  Install with: pip install trimesh")
        return None


def test_file_structure():
    """Basic file structure test."""
    print("\n" + "="*60)
    print("TEST 2: File Structure Check")
    print("="*60)
    
    models = [
        'assets/models/Anime_School_Teacher.GLB',
        'assets/models/old_female.glb'
    ]
    
    for model_path in models:
        print(f"\n{model_path}:")
        
        if not os.path.exists(model_path):
            print("  ✗ File not found")
            continue
        
        size = os.path.getsize(model_path)
        print(f"  Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
        
        with open(model_path, 'rb') as f:
            magic = f.read(12)
            
        if magic[:4] == b'glTF':
            print("  ✓ Valid GLB file signature")
            
            import struct
            version = struct.unpack('<I', magic[4:8])[0]
            length = struct.unpack('<I', magic[8:12])[0]
            print(f"  GLB version: {version}")
            print(f"  Declared length: {length:,} bytes")
            
            if length != size:
                print(f"  ⚠ Size mismatch (expected {length}, got {size})")
            else:
                print(f"  ✓ File size matches header")
        else:
            print(f"  ✗ Invalid signature: {magic[:4]}")


def main():
    print("="*60)
    print("GLB MODEL DIAGNOSTIC TOOL")
    print("="*60)
    
    if not os.path.exists('assets/models'):
        print("✗ ERROR: assets/models not found")
        print("  Current directory:", os.getcwd())
        return
    
    print("Working directory:", os.getcwd())
    
    print("\nGLB files found:")
    for f in os.listdir('assets/models'):
        if f.lower().endswith(('.glb', '.gltf')):
            path = os.path.join('assets/models', f)
            size = os.path.getsize(path)
            print(f"  - {f} ({size/1024/1024:.1f} MB)")
    
    test_file_structure()
    trimesh_result = test_with_trimesh()
    
    print("\n" + "="*60)
    print("DIAGNOSIS")
    print("="*60)
    
    if trimesh_result is None:
        print("⚠ Install trimesh: pip install trimesh")
    elif trimesh_result:
        print("✓ Models are VALID GLB files")
        print("\nIssue is likely Panda3D compatibility or positioning")
    else:
        print("✗ Models are INVALID/CORRUPTED")


if __name__ == '__main__':
    main()
