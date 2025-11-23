#!/usr/bin/env python3
"""
Test Panda3D basic functionality.
This verifies Panda3D is installed and can create a window.
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, CardMaker


class TestApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set window title
        props = WindowProperties()
        props.setTitle("Panda3D Test - Phase 2.0")
        self.win.requestProperties(props)

        # Disable default mouse camera
        self.disableMouse()

        # Set camera position
        self.camera.setPos(0, -10, 0)
        self.camera.lookAt(0, 0, 0)

        # Create a simple box
        card = CardMaker('test_card')
        card.setFrame(-1, 1, -1, 1)
        card_np = self.render.attachNewNode(card.generate())
        card_np.setColor(0.5, 0.8, 0.5, 1)

        print("✓ Panda3D window created")
        print("✓ Simple geometry rendered")
        print("Press ESC to close")


if __name__ == '__main__':
    app = TestApp()
    app.run()
