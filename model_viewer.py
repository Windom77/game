#!/usr/bin/env python3
"""
GLB Model Viewer for Character Customization.

A lightweight 3D viewer for quickly previewing GLB models during
character customization, without needing to launch the full game.

Usage:
    python model_viewer.py                           # Opens file picker
    python model_viewer.py model.glb                 # Load specific model
    python model_viewer.py --compare a.glb b.glb     # Compare two models

Controls:
    Left Mouse Drag  - Rotate model
    Right Mouse Drag - Pan camera
    Mouse Scroll     - Zoom in/out
    R                - Reset view
    L                - Toggle lighting mode
    W                - Toggle wireframe
    G                - Toggle grid floor
    T                - Toggle turntable (auto-rotate)
    S                - Screenshot
    Space            - Toggle between models (compare mode)
    ESC              - Close viewer
"""

import sys
import os
import argparse
from datetime import datetime

# Panda3D imports
try:
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from panda3d.core import (
        WindowProperties, AmbientLight, DirectionalLight, PointLight,
        Vec3, Vec4, Point3, NodePath, LVector3f,
        GeomNode, Geom, GeomVertexData, GeomVertexFormat,
        GeomTriangles, GeomVertexWriter, GeomLines,
        CardMaker, TextNode, Filename,
        RenderModeAttrib, AntialiasAttrib,
        loadPrcFileData
    )
    from direct.gui.OnscreenText import OnscreenText
    from direct.gui.DirectGui import DirectButton, DirectFrame
    PANDA3D_AVAILABLE = True
except ImportError:
    PANDA3D_AVAILABLE = False
    print("Error: Panda3D not installed. Install with: pip install panda3d")

# Trimesh for GLB loading
try:
    import trimesh
    import numpy as np
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    print("Warning: trimesh not installed. Install with: pip install trimesh")


# Configure Panda3D before ShowBase init
if PANDA3D_AVAILABLE:
    loadPrcFileData('', 'window-title GLB Model Viewer')
    loadPrcFileData('', 'win-size 900 700')
    loadPrcFileData('', 'sync-video #t')


class OrbitCamera:
    """Orbit camera controller for model viewing."""

    def __init__(self, base, distance=5.0, heading=0, pitch=-20):
        self.base = base
        self.distance = distance
        self.min_distance = 0.5
        self.max_distance = 50.0

        self.heading = heading  # Rotation around Y (horizontal)
        self.pitch = pitch      # Rotation around X (vertical)
        self.target = Point3(0, 0, 0)  # Look-at point

        # Mouse state
        self.is_rotating = False
        self.is_panning = False
        self.last_mouse_pos = None

        self.update_camera()

    def update_camera(self):
        """Update camera position based on orbit parameters."""
        import math

        # Convert to radians
        h_rad = math.radians(self.heading)
        p_rad = math.radians(self.pitch)

        # Calculate camera position on sphere around target
        x = self.distance * math.cos(p_rad) * math.sin(h_rad)
        y = -self.distance * math.cos(p_rad) * math.cos(h_rad)
        z = self.distance * math.sin(p_rad)

        # Set camera position and look at target
        self.base.camera.setPos(
            self.target.x + x,
            self.target.y + y,
            self.target.z + z
        )
        self.base.camera.lookAt(self.target)

    def rotate(self, delta_h, delta_p):
        """Rotate camera around target."""
        self.heading += delta_h
        self.pitch = max(-89, min(89, self.pitch + delta_p))
        self.update_camera()

    def pan(self, delta_x, delta_y):
        """Pan camera (move target)."""
        import math

        # Get camera right and up vectors
        h_rad = math.radians(self.heading)

        right = Vec3(math.cos(h_rad), math.sin(h_rad), 0)
        up = Vec3(0, 0, 1)

        # Scale by distance for consistent feel
        scale = self.distance * 0.002

        self.target += right * delta_x * scale
        self.target += up * delta_y * scale
        self.update_camera()

    def zoom(self, delta):
        """Zoom camera in/out."""
        self.distance *= (1.0 - delta * 0.1)
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        self.update_camera()

    def reset(self, target=None, distance=None):
        """Reset camera to default view."""
        self.heading = 30
        self.pitch = -20
        if target is not None:
            self.target = target
        else:
            self.target = Point3(0, 0, 0)
        if distance is not None:
            self.distance = distance
        self.update_camera()

    def frame_model(self, bounds_min, bounds_max):
        """Auto-frame camera to fit model in view."""
        # Calculate center and size
        center = (bounds_min + bounds_max) * 0.5
        size = bounds_max - bounds_min
        max_dim = max(size.x, size.y, size.z)

        # Set target to model center
        self.target = Point3(center.x, center.y, center.z)

        # Set distance to fit model
        self.distance = max_dim * 2.0
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))

        self.update_camera()


class ModelViewer(ShowBase):
    """3D Model Viewer application."""

    def __init__(self, model_path=None, compare_path=None):
        ShowBase.__init__(self)

        # State
        self.current_model = None
        self.compare_model = None
        self.current_file = None
        self.compare_file = None
        self.model_a = None
        self.model_b = None
        self.showing_model_a = True

        # Display options
        self.wireframe_mode = False
        self.show_grid = True
        self.turntable_active = False
        self.lighting_mode = 0  # 0=normal, 1=bright, 2=dark

        # Setup
        self.setup_window()
        self.setup_camera()
        self.setup_lighting()
        self.setup_controls()
        self.setup_ui()
        self.create_grid()

        # Load models if provided
        if model_path:
            self.load_model(model_path)
        if compare_path:
            self.load_compare_model(compare_path)

        # Update task
        self.taskMgr.add(self.update_task, 'update')

        print("\n" + "=" * 50)
        print("GLB Model Viewer - Controls:")
        print("=" * 50)
        print("  Left Drag   - Rotate model")
        print("  Right Drag  - Pan camera")
        print("  Scroll      - Zoom in/out")
        print("  R           - Reset view")
        print("  L           - Cycle lighting")
        print("  W           - Toggle wireframe")
        print("  G           - Toggle grid")
        print("  T           - Toggle turntable")
        print("  S           - Screenshot")
        print("  Space       - Toggle models (compare)")
        print("  ESC         - Close")
        print("=" * 50 + "\n")

    def setup_window(self):
        """Configure window properties."""
        props = WindowProperties()
        props.setTitle("GLB Model Viewer")
        self.win.requestProperties(props)

        # Set background color (neutral gray)
        self.setBackgroundColor(0.25, 0.25, 0.28, 1.0)

    def setup_camera(self):
        """Setup orbit camera."""
        self.disableMouse()
        self.orbit_cam = OrbitCamera(self, distance=5.0)

    def setup_lighting(self):
        """Setup scene lighting."""
        self.lights = []

        # Ambient light
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.3, 0.3, 0.32, 1))
        self.ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(self.ambient_np)
        self.lights.append(self.ambient_np)

        # Key light (main directional)
        key = DirectionalLight('key')
        key.setColor(Vec4(0.9, 0.88, 0.85, 1))
        self.key_np = self.render.attachNewNode(key)
        self.key_np.setHpr(-45, -45, 0)
        self.render.setLight(self.key_np)
        self.lights.append(self.key_np)

        # Fill light (softer, opposite side)
        fill = DirectionalLight('fill')
        fill.setColor(Vec4(0.4, 0.42, 0.45, 1))
        self.fill_np = self.render.attachNewNode(fill)
        self.fill_np.setHpr(135, -30, 0)
        self.render.setLight(self.fill_np)
        self.lights.append(self.fill_np)

        # Rim light (back light for edge definition)
        rim = DirectionalLight('rim')
        rim.setColor(Vec4(0.3, 0.3, 0.35, 1))
        self.rim_np = self.render.attachNewNode(rim)
        self.rim_np.setHpr(0, 45, 0)
        self.render.setLight(self.rim_np)
        self.lights.append(self.rim_np)

    def setup_controls(self):
        """Setup mouse and keyboard controls."""
        # Mouse controls
        self.accept('mouse1', self.on_mouse_press, ['left'])
        self.accept('mouse1-up', self.on_mouse_release, ['left'])
        self.accept('mouse3', self.on_mouse_press, ['right'])
        self.accept('mouse3-up', self.on_mouse_release, ['right'])
        self.accept('wheel_up', self.on_scroll, [1])
        self.accept('wheel_down', self.on_scroll, [-1])

        # Keyboard controls
        self.accept('r', self.reset_view)
        self.accept('l', self.cycle_lighting)
        self.accept('w', self.toggle_wireframe)
        self.accept('g', self.toggle_grid)
        self.accept('t', self.toggle_turntable)
        self.accept('s', self.take_screenshot)
        self.accept('space', self.toggle_compare)
        self.accept('escape', sys.exit)

        # File loading
        self.accept('o', self.open_file_dialog)

    def setup_ui(self):
        """Setup on-screen UI elements."""
        # Title/filename display
        self.title_text = OnscreenText(
            text="No model loaded - Press O to open",
            pos=(0, 0.92),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            align=TextNode.ACenter
        )

        # Controls hint
        self.hint_text = OnscreenText(
            text="[O] Open  [R] Reset  [W] Wire  [L] Light  [G] Grid  [T] Rotate  [S] Screenshot",
            pos=(0, -0.95),
            scale=0.04,
            fg=(0.7, 0.7, 0.7, 1),
            align=TextNode.ACenter
        )

        # Stats display (vertices, etc.)
        self.stats_text = OnscreenText(
            text="",
            pos=(-1.3, 0.85),
            scale=0.04,
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ALeft
        )

        # Compare mode indicator
        self.compare_text = OnscreenText(
            text="",
            pos=(1.3, 0.85),
            scale=0.045,
            fg=(1, 0.8, 0.2, 1),
            align=TextNode.ARight
        )

    def create_grid(self):
        """Create a reference grid floor."""
        # Create grid using lines
        grid_node = GeomNode('grid')

        vformat = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('grid', vformat, Geom.UHStatic)

        vertex_writer = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

        lines = GeomLines(Geom.UHStatic)

        grid_size = 10
        grid_step = 1.0
        grid_color = (0.4, 0.4, 0.4, 0.5)
        axis_color_x = (0.8, 0.3, 0.3, 0.8)
        axis_color_y = (0.3, 0.8, 0.3, 0.8)

        vertex_idx = 0

        # Grid lines parallel to X axis
        for i in range(-grid_size, grid_size + 1):
            y = i * grid_step
            color = axis_color_y if i == 0 else grid_color

            vertex_writer.addData3f(-grid_size * grid_step, y, 0)
            color_writer.addData4f(*color)
            vertex_writer.addData3f(grid_size * grid_step, y, 0)
            color_writer.addData4f(*color)

            lines.addVertices(vertex_idx, vertex_idx + 1)
            vertex_idx += 2

        # Grid lines parallel to Y axis
        for i in range(-grid_size, grid_size + 1):
            x = i * grid_step
            color = axis_color_x if i == 0 else grid_color

            vertex_writer.addData3f(x, -grid_size * grid_step, 0)
            color_writer.addData4f(*color)
            vertex_writer.addData3f(x, grid_size * grid_step, 0)
            color_writer.addData4f(*color)

            lines.addVertices(vertex_idx, vertex_idx + 1)
            vertex_idx += 2

        lines.closePrimitive()

        geom = Geom(vdata)
        geom.addPrimitive(lines)
        grid_node.addGeom(geom)

        self.grid_np = self.render.attachNewNode(grid_node)
        self.grid_np.setTwoSided(True)
        self.grid_np.setTransparency(True)

    def load_model(self, filepath):
        """Load a GLB model from file."""
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            self.title_text.setText(f"Error: File not found")
            return False

        print(f"Loading: {filepath}")

        # Remove existing model
        if self.current_model:
            self.current_model.removeNode()
            self.current_model = None

        # Load with trimesh
        model_np = self._load_glb_with_trimesh(filepath)

        if model_np:
            self.current_model = model_np
            self.current_file = filepath
            self.model_a = model_np

            # Frame camera to model
            bounds = model_np.getTightBounds()
            if bounds:
                self.orbit_cam.frame_model(bounds[0], bounds[1])

            # Update UI
            filename = os.path.basename(filepath)
            self.title_text.setText(filename)

            # Get stats
            self._update_stats()

            print(f"Loaded: {filename}")
            return True
        else:
            self.title_text.setText("Error loading model")
            return False

    def load_compare_model(self, filepath):
        """Load a second model for comparison."""
        if not os.path.exists(filepath):
            print(f"Error: Compare file not found: {filepath}")
            return False

        print(f"Loading compare model: {filepath}")

        # Load with trimesh
        model_np = self._load_glb_with_trimesh(filepath)

        if model_np:
            self.compare_model = model_np
            self.compare_file = filepath
            self.model_b = model_np

            # Hide compare model initially
            model_np.hide()

            # Update compare text
            self.compare_text.setText("[Space] Toggle A/B")

            print(f"Compare model loaded. Press Space to toggle.")
            return True
        return False

    def _load_glb_with_trimesh(self, filepath):
        """Load GLB using trimesh and convert to Panda3D geometry."""
        if not TRIMESH_AVAILABLE:
            print("Error: trimesh not available")
            return None

        try:
            # Load with trimesh
            scene = trimesh.load(filepath)

            # Collect meshes
            all_vertices = []
            all_normals = []
            all_faces = []
            vertex_offset = 0

            if isinstance(scene, trimesh.Scene):
                meshes = list(scene.geometry.values())
            else:
                meshes = [scene]

            for mesh in meshes:
                if not hasattr(mesh, 'vertices') or not hasattr(mesh, 'faces'):
                    continue

                verts = np.array(mesh.vertices)
                faces = np.array(mesh.faces)

                if len(verts) == 0 or len(faces) == 0:
                    continue

                # Get normals
                if hasattr(mesh, 'vertex_normals') and mesh.vertex_normals is not None:
                    norms = np.array(mesh.vertex_normals)
                else:
                    norms = np.zeros_like(verts)
                    norms[:, 2] = 1.0

                # Offset faces
                offset_faces = faces + vertex_offset

                all_vertices.append(verts)
                all_normals.append(norms)
                all_faces.append(offset_faces)
                vertex_offset += len(verts)

            if not all_vertices:
                print("Error: No valid geometry found")
                return None

            # Combine all meshes
            vertices = np.vstack(all_vertices)
            normals = np.vstack(all_normals)
            faces = np.vstack(all_faces)

            # Center at origin
            center = vertices.mean(axis=0)
            vertices = vertices - center

            # Create Panda3D geometry
            geom_node = GeomNode('model')

            vformat = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData('vertices', vformat, Geom.UHStatic)
            vdata.setNumRows(len(vertices))

            vertex_writer = GeomVertexWriter(vdata, 'vertex')
            normal_writer = GeomVertexWriter(vdata, 'normal')

            for i, vert in enumerate(vertices):
                # Swap Y and Z for Panda3D coordinate system
                vertex_writer.addData3f(float(vert[0]), float(vert[2]), float(vert[1]))
                n = normals[i]
                normal_writer.addData3f(float(n[0]), float(n[2]), float(n[1]))

            # Create triangles
            tris = GeomTriangles(Geom.UHStatic)
            for face in faces:
                tris.addVertices(int(face[0]), int(face[1]), int(face[2]))
            tris.closePrimitive()

            geom = Geom(vdata)
            geom.addPrimitive(tris)
            geom_node.addGeom(geom)

            # Create NodePath
            model_np = self.render.attachNewNode(geom_node)

            # Default color (will be overridden by materials if present)
            model_np.setColor(0.8, 0.8, 0.8, 1.0)

            # Store vertex count for stats
            model_np.setPythonTag('vertex_count', len(vertices))
            model_np.setPythonTag('face_count', len(faces))

            return model_np

        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _update_stats(self):
        """Update stats display."""
        if not self.current_model:
            self.stats_text.setText("")
            return

        verts = self.current_model.getPythonTag('vertex_count') or 0
        faces = self.current_model.getPythonTag('face_count') or 0

        self.stats_text.setText(f"Vertices: {verts:,}\nFaces: {faces:,}")

    # === Mouse Controls ===

    def on_mouse_press(self, button):
        """Handle mouse button press."""
        if button == 'left':
            self.orbit_cam.is_rotating = True
        elif button == 'right':
            self.orbit_cam.is_panning = True

        if self.mouseWatcherNode.hasMouse():
            self.orbit_cam.last_mouse_pos = (
                self.mouseWatcherNode.getMouseX(),
                self.mouseWatcherNode.getMouseY()
            )

    def on_mouse_release(self, button):
        """Handle mouse button release."""
        if button == 'left':
            self.orbit_cam.is_rotating = False
        elif button == 'right':
            self.orbit_cam.is_panning = False

    def on_scroll(self, direction):
        """Handle mouse scroll."""
        self.orbit_cam.zoom(direction)

    # === Keyboard Controls ===

    def reset_view(self):
        """Reset camera to default view."""
        if self.current_model:
            bounds = self.current_model.getTightBounds()
            if bounds:
                self.orbit_cam.frame_model(bounds[0], bounds[1])
        else:
            self.orbit_cam.reset()
        print("View reset")

    def cycle_lighting(self):
        """Cycle through lighting presets."""
        self.lighting_mode = (self.lighting_mode + 1) % 3

        if self.lighting_mode == 0:
            # Normal lighting
            self.ambient_np.node().setColor(Vec4(0.3, 0.3, 0.32, 1))
            self.key_np.node().setColor(Vec4(0.9, 0.88, 0.85, 1))
            print("Lighting: Normal")
        elif self.lighting_mode == 1:
            # Bright lighting
            self.ambient_np.node().setColor(Vec4(0.5, 0.5, 0.52, 1))
            self.key_np.node().setColor(Vec4(1.2, 1.18, 1.15, 1))
            print("Lighting: Bright")
        else:
            # Dark/moody lighting
            self.ambient_np.node().setColor(Vec4(0.15, 0.15, 0.18, 1))
            self.key_np.node().setColor(Vec4(0.6, 0.58, 0.55, 1))
            print("Lighting: Dark")

    def toggle_wireframe(self):
        """Toggle wireframe rendering."""
        self.wireframe_mode = not self.wireframe_mode

        if self.wireframe_mode:
            self.render.setRenderModeWireframe()
            print("Wireframe: ON")
        else:
            self.render.setRenderModeFilled()
            print("Wireframe: OFF")

    def toggle_grid(self):
        """Toggle grid visibility."""
        self.show_grid = not self.show_grid

        if self.show_grid:
            self.grid_np.show()
            print("Grid: ON")
        else:
            self.grid_np.hide()
            print("Grid: OFF")

    def toggle_turntable(self):
        """Toggle auto-rotation."""
        self.turntable_active = not self.turntable_active
        print(f"Turntable: {'ON' if self.turntable_active else 'OFF'}")

    def toggle_compare(self):
        """Toggle between comparison models."""
        if not self.compare_model:
            print("No compare model loaded")
            return

        self.showing_model_a = not self.showing_model_a

        if self.showing_model_a:
            self.model_a.show()
            self.model_b.hide()
            self.title_text.setText(f"A: {os.path.basename(self.current_file)}")
        else:
            self.model_a.hide()
            self.model_b.show()
            self.title_text.setText(f"B: {os.path.basename(self.compare_file)}")

        print(f"Showing model {'A' if self.showing_model_a else 'B'}")

    def take_screenshot(self):
        """Save screenshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

        # Save to characterdev folder if it exists, otherwise current dir
        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "models", "characterdev"
        )
        if os.path.exists(output_dir):
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename

        self.screenshot(filepath, defaultFilename=False)
        print(f"Screenshot saved: {filepath}")

    def open_file_dialog(self):
        """Open file dialog to load a model."""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()

            initial_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "assets", "models"
            )
            if not os.path.exists(initial_dir):
                initial_dir = os.path.dirname(os.path.abspath(__file__))

            filepath = filedialog.askopenfilename(
                title="Select GLB Model",
                initialdir=initial_dir,
                filetypes=[
                    ("GLB Files", "*.glb"),
                    ("GLTF Files", "*.gltf"),
                    ("All Files", "*.*")
                ]
            )

            root.destroy()

            if filepath:
                self.load_model(filepath)

        except Exception as e:
            print(f"Error opening file dialog: {e}")

    # === Update Loop ===

    def update_task(self, task):
        """Main update loop."""
        # Handle mouse movement for camera control
        if self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()

            if self.orbit_cam.last_mouse_pos:
                delta_x = (mouse_x - self.orbit_cam.last_mouse_pos[0]) * 100
                delta_y = (mouse_y - self.orbit_cam.last_mouse_pos[1]) * 100

                if self.orbit_cam.is_rotating:
                    self.orbit_cam.rotate(-delta_x, delta_y)
                elif self.orbit_cam.is_panning:
                    self.orbit_cam.pan(-delta_x, delta_y)

            self.orbit_cam.last_mouse_pos = (mouse_x, mouse_y)

        # Turntable auto-rotation
        if self.turntable_active:
            self.orbit_cam.heading += 0.5
            self.orbit_cam.update_camera()

        return Task.cont


def main():
    """Main entry point."""
    if not PANDA3D_AVAILABLE:
        print("Error: Panda3D is required but not installed.")
        print("Install with: pip install panda3d")
        return 1

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="GLB Model Viewer for Character Customization"
    )
    parser.add_argument(
        'model',
        nargs='?',
        help='Path to GLB model file'
    )
    parser.add_argument(
        '--compare', '-c',
        help='Second model for comparison'
    )

    args = parser.parse_args()

    # Create viewer
    viewer = ModelViewer(
        model_path=args.model,
        compare_path=args.compare
    )

    # Run
    viewer.run()

    return 0


if __name__ == '__main__':
    sys.exit(main())
