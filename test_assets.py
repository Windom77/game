#!/usr/bin/env python3
"""
Test asset loading for Phase 2.0.
Verifies background and character models load correctly.
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, AmbientLight
import os


class AssetTest(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        props = WindowProperties()
        props.setTitle("Asset Loading Test")
        self.win.requestProperties(props)

        self.disableMouse()
        self.camera.setPos(0, -10, 3)
        self.camera.lookAt(0, 0, 0)

        # Test 1: Load background image
        print("Test 1: Loading background...")
        bg_path = 'assets/backgrounds/library.jpg'
        if os.path.exists(bg_path):
            bg_tex = self.loader.loadTexture(bg_path)
            print(f"✓ Background loaded: {bg_tex.getXSize()}x{bg_tex.getYSize()}")
        else:
            print(f"✗ FAIL: Background not found at {bg_path}")
            return

        # Test 2: Load young character model
        print("\nTest 2: Loading young character model...")
        young_path = 'assets/models/Anime_School_Teacher.GLB'
        if os.path.exists(young_path):
            young_model = self.loader.loadModel(young_path)
            young_model.reparentTo(self.render)
            young_model.setPos(-3, 0, 0)
            young_model.setScale(0.5)
            print(f"✓ Young model loaded: {young_model}")
        else:
            print(f"✗ FAIL: Young model not found at {young_path}")
            return

        # Test 3: Load older character model
        print("\nTest 3: Loading older character model...")
        old_path = 'assets/models/old_female.glb'
        if os.path.exists(old_path):
            old_model = self.loader.loadModel(old_path)
            old_model.reparentTo(self.render)
            old_model.setPos(3, 0, 0)
            old_model.setScale(0.5)
            print(f"✓ Old model loaded: {old_model}")
        else:
            print(f"✗ FAIL: Old model not found at {old_path}")
            return

        # Test 4: Apply color tints
        print("\nTest 4: Testing color tints...")
        young_model.setColor(0.3, 0.6, 0.4, 1)  # Green
        old_model.setColor(0.55, 0.35, 0.2, 1)  # Brown
        print("✓ Color tints applied")

        # Add lighting
        alight = AmbientLight('ambient')
        alight.setColor((0.5, 0.5, 0.5, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        print("\n✓✓✓ ALL ASSET TESTS PASSED ✓✓✓")
        print("You should see 2 character models with color tints")
        print("Press ESC to close")


if __name__ == '__main__':
    app = AssetTest()
    app.run()
