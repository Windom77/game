#!/usr/bin/env python3
"""
GLB Model Diagnostic Tool - FIXED VERSION
Tests if GLB files are valid and can be loaded properly.
"""

import os
import sys


def test_with_trimesh():
    """Test loading with trimesh (most reliable test)."""
    print("\n" + "=" * 60)
    print("TEST 1: Trimesh Loader")
    print("=" * 60)

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
                        print("  ✗ ERROR: No vertices found - INVALID MODEL")
                        return False
                    else:
                        print("  ✓ Model has valid geometry")

                    # Get bounds
                    bounds = scene.bounds
                    if bounds is not None and len(bounds) == 2:
                        min_pt = bounds[0]
                        max_pt = bounds[1]
                        size = max_pt - min_pt
                        print(f"  Bounds min: [{min_pt[0]:.2f}, {min_pt[1]:.2f}, {min_pt[2]:.2f}]")
                        print(f"  Bounds max: [{max_pt[0]:.2f}, {max_pt[1]:.2f}, {max_pt[2]:.2f}]")
                        print(f"  Size: [{size[0]:.2f}, {size[1]:.2f}, {size[2]:.2f}]")

                        # Check if reasonable
                        if max(size) > 1000:
                            print(f"  ⚠ WARNING: Model is HUGE (max dimension: {max(size):.2f})")
                        elif max(size) < 0.01:
                            print(f"  ⚠ WARNING: Model is TINY (max dimension: {max(size):.6f})")
                        else:
                            print(f"  ✓ Size is reasonable")

                return True

            except Exception as e:
                print(f"  ✗ Error: {e}")
                import traceback
                traceback.print_exc()
                return False

        return True

    except ImportError:
        print("✗ Trimesh not installed")
        print("  Install with: pip install trimesh")
        return None


def test_file_structure():
    """Basic file structure test."""
    print("\n" + "=" * 60)
    print("TEST 2: File Structure Check")
    print("=" * 60)

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
        print(f"  Size: {size:,} bytes ({size / 1024 / 1024:.1f} MB)")

        # Read first few bytes to check file signature
        with open(model_path, 'rb') as f:
            magic = f.read(12)

        if magic[:4] == b'glTF':
            print("  ✓ Valid GLB file signature")

            # Parse GLB header
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
            print(f"  ✗ Invalid file signature: {magic[:4]}")
            print(f"     (Expected b'glTF', got {magic[:4]})")


def main():
    """Run all tests."""
    print("=" * 60)
    print("GLB MODEL DIAGNOSTIC TOOL")
    print("=" * 60)

    # Check directory
    if not os.path.exists('assets/models'):
        print("✗ ERROR: assets/models not found")
        print("  Current directory:", os.getcwd())
        print("  Run from game/ directory")
        return

    print("Working directory:", os.getcwd())

    # List files
    print("\nGLB files found:")
    for f in os.listdir('assets/models'):
        if f.lower().endswith(('.glb', '.gltf')):
            path = os.path.join('assets/models', f)
            size = os.path.getsize(path)
            print(f"  - {f} ({size:,} bytes, {size / 1024 / 1024:.1f} MB)")

    # Run tests
    test_file_structure()
    trimesh_result = test_with_trimesh()

    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)

    if trimesh_result is None:
        print("⚠ Cannot fully diagnose - install trimesh:")
        print("  pip install trimesh")
    elif trimesh_result:
        print("✓ Models appear to be VALID GLB files with geometry")
        print("\nThe issue is likely:")
        print("  1. Panda3D path resolution problem")
        print("  2. Model scale/positioning in scene")
        print("  3. Rigging causing transform issues")
    else:
        print("✗ Models are INVALID or CORRUPTED")
        print("\nRecommendation:")
        print("  - Re-download or regenerate the GLB models")
        print("  - Use simpler models without rigging")


if __name__ == '__main__':
    main()