#!/usr/bin/env python3
"""
Test the 3D scene for Phase 2.0.
Verifies scene creation with table and characters.
"""
from direct.showbase.ShowBase import ShowBase
from scene_3d import Scene3D


class TestScene(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.scene = Scene3D(self)
        print("✓ Scene created successfully")
        print("Characters loaded:", list(self.scene.characters.keys()))
        print("Press ESC to close")


if __name__ == '__main__':
    app = TestScene()
    app.run()
