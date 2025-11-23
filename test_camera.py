#!/usr/bin/env python3
"""
Test camera focus system for Phase 2.0.
Demonstrates smooth camera rotation to face each character.
"""
from direct.showbase.ShowBase import ShowBase
from scene_3d import Scene3D


class CameraTest(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.scene = Scene3D(self)

        # Test camera focusing
        print("Testing camera focus...")
        self.taskMgr.doMethodLater(2, self.focus_major, 'focus_major')
        self.taskMgr.doMethodLater(4, self.focus_lady, 'focus_lady')
        self.taskMgr.doMethodLater(6, self.focus_clara, 'focus_clara')
        self.taskMgr.doMethodLater(8, self.focus_thomas, 'focus_thomas')
        self.taskMgr.doMethodLater(10, self.reset, 'reset')

        print("Watch camera rotate through all characters over 10 seconds")
        print("Press ESC to close")

    def focus_major(self, task):
        print("→ Focusing Major")
        self.scene.focus_character('major')
        return task.done

    def focus_lady(self, task):
        print("→ Focusing Lady")
        self.scene.focus_character('lady')
        return task.done

    def focus_clara(self, task):
        print("→ Focusing Clara")
        self.scene.focus_character('maid')
        return task.done

    def focus_thomas(self, task):
        print("→ Focusing Thomas")
        self.scene.focus_character('student')
        return task.done

    def reset(self, task):
        print("→ Reset to neutral")
        self.scene.reset_camera()
        return task.done


if __name__ == '__main__':
    app = CameraTest()
    app.run()
