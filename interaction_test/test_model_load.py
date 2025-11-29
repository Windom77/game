#!/usr/bin/env python3
"""Quick test to load old_female.glb and check bounds."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData

class QuickTest(ShowBase):
    def __init__(self):
        # Configure panda3d-gltf
        loadPrcFileData("", "load-file-type p3assimp")

        ShowBase.__init__(self)

        # Load RPmeAvatar.glb
        parent_dir = Path(__file__).parent.parent
        model_path = parent_dir / "assets" / "models" / "RPmeAvatar.glb"

        print("=" * 60)
        print(f"Testing: {model_path}")
        print(f"Exists: {model_path.exists()}")
        print("=" * 60)

        if not model_path.exists():
            print("ERROR: File not found!")
            sys.exit(1)

        # Load the model
        print("\nLoading model...")
        try:
            model = self.loader.loadModel(str(model_path))

            if model and not model.isEmpty():
                print("✓ Model loaded successfully!")

                # Get bounds
                bounds = model.getTightBounds()
                if bounds:
                    min_pt, max_pt = bounds
                    width = max_pt.x - min_pt.x
                    depth = max_pt.y - min_pt.y
                    height = max_pt.z - min_pt.z

                    print(f"\nBOUNDS:")
                    print(f"  Min: ({min_pt.x:.3f}, {min_pt.y:.3f}, {min_pt.z:.3f})")
                    print(f"  Max: ({max_pt.x:.3f}, {max_pt.y:.3f}, {max_pt.z:.3f})")
                    print(f"  Dimensions: W={width:.3f}, D={depth:.3f}, H={height:.3f}")

                    # Check if reasonable
                    if width > 100 or depth > 100 or height > 100:
                        print("  ⚠ WARNING: Model is very large! (>100 units)")
                    elif width < 0.01 or depth < 0.01 or height < 0.01:
                        print("  ⚠ WARNING: Model is very small! (<0.01 units)")
                    else:
                        print("  ✓ Dimensions look reasonable")
                else:
                    print("  ⚠ No bounds available")

                # Attach to render for display test
                model.reparentTo(self.render)

                # Position camera
                self.disableMouse()
                self.camera.setPos(0, -3.0, 1.0)
                self.camera.lookAt(0, 0, 0.5)

                print("\n✓ Model attached to scene")
                print("Camera positioned at (0, -3.0, 1.0)")
                print("\nClosing in 3 seconds...")

                # Close after 3 seconds
                self.taskMgr.doMethodLater(3.0, lambda task: sys.exit(0), 'quit')
            else:
                print("⚠ Model is empty!")
                sys.exit(1)

        except Exception as e:
            print(f"⚠ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    app = QuickTest()
    app.run()
