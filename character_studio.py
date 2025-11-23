#!/usr/bin/env python3
"""
Character Customization Studio - Unified Editor with Real-Time 3D Preview.

A complete character customization tool that combines material editing with
an embedded real-time 3D viewer. Changes to material colors are instantly
reflected in the 3D preview without saving or reloading.

Usage:
    python character_studio.py

Requirements:
    - pygltflib (pip install pygltflib)
    - panda3d (pip install panda3d)
    - trimesh (pip install trimesh)
    - tkinter (usually included with Python)

Layout:
    +------------------------------------------+
    |  Character Customization Studio          |
    +----------------+-------------------------+
    |   Controls     |     3D Preview          |
    |   (~40%)       |       (~60%)            |
    |                |                         |
    |  [Materials]   |    [Embedded Panda3D]   |
    |  [Sliders]     |                         |
    |  [Presets]     |    [Real-time updates]  |
    |                |                         |
    +----------------+-------------------------+
    |  [Reset] [Undo] [Save As] [Quick Save]  |
    +------------------------------------------+
"""

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import os
import sys
import json
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict
import math

# Check dependencies
PYGLTFLIB_AVAILABLE = False
PANDA3D_AVAILABLE = False
TRIMESH_AVAILABLE = False

try:
    from pygltflib import GLTF2
    PYGLTFLIB_AVAILABLE = True
except ImportError:
    print("Warning: pygltflib not installed. Install with: pip install pygltflib")

try:
    import numpy as np
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    print("Warning: trimesh not installed. Install with: pip install trimesh")

# Panda3D configuration must happen before imports
try:
    from panda3d.core import loadPrcFileData
    # Configure for embedded window
    loadPrcFileData('', 'window-type none')  # Start without window, create later
    loadPrcFileData('', 'audio-library-name null')  # Disable audio
    loadPrcFileData('', 'sync-video #f')

    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
    from panda3d.core import (
        WindowProperties, AmbientLight, DirectionalLight,
        Vec3, Vec4, Point3, NodePath,
        GeomNode, Geom, GeomVertexData, GeomVertexFormat,
        GeomTriangles, GeomVertexWriter, GeomLines,
        FrameBufferProperties, GraphicsPipe, GraphicsOutput
    )
    PANDA3D_AVAILABLE = True
except ImportError:
    print("Warning: Panda3D not installed. Install with: pip install panda3d")


# ============================================================================
# Data Classes & Presets
# ============================================================================

@dataclass
class MaterialInfo:
    """Information about a material in the GLB file."""
    index: int
    name: str
    base_color: List[float]  # [R, G, B, A]
    original_color: List[float]
    enabled: bool = True


@dataclass
class ColorPreset:
    """Predefined color preset."""
    name: str
    color: List[float]  # [R, G, B, A]


# Skin tone presets
SKIN_PRESETS = [
    ColorPreset("Pale", [0.95, 0.87, 0.82, 1.0]),
    ColorPreset("Fair", [0.92, 0.78, 0.68, 1.0]),
    ColorPreset("Medium", [0.82, 0.64, 0.52, 1.0]),
    ColorPreset("Tan", [0.76, 0.57, 0.45, 1.0]),
    ColorPreset("Brown", [0.55, 0.38, 0.28, 1.0]),
    ColorPreset("Dark", [0.36, 0.24, 0.18, 1.0]),
]

# Hair color presets
HAIR_PRESETS = [
    ColorPreset("Black", [0.05, 0.05, 0.05, 1.0]),
    ColorPreset("Dark Brown", [0.20, 0.12, 0.08, 1.0]),
    ColorPreset("Brown", [0.35, 0.22, 0.15, 1.0]),
    ColorPreset("Auburn", [0.50, 0.25, 0.15, 1.0]),
    ColorPreset("Blonde", [0.85, 0.70, 0.45, 1.0]),
    ColorPreset("Red", [0.60, 0.20, 0.10, 1.0]),
    ColorPreset("Gray", [0.60, 0.60, 0.60, 1.0]),
    ColorPreset("White", [0.95, 0.95, 0.95, 1.0]),
]

# Clothing color presets
CLOTHING_PRESETS = [
    ColorPreset("Black", [0.08, 0.08, 0.08, 1.0]),
    ColorPreset("White", [0.95, 0.95, 0.95, 1.0]),
    ColorPreset("Navy", [0.10, 0.15, 0.30, 1.0]),
    ColorPreset("Burgundy", [0.45, 0.10, 0.15, 1.0]),
    ColorPreset("Forest Green", [0.15, 0.30, 0.15, 1.0]),
    ColorPreset("Victorian Purple", [0.35, 0.20, 0.40, 1.0]),
    ColorPreset("Maid Gray", [0.40, 0.40, 0.42, 1.0]),
    ColorPreset("Cream", [0.95, 0.92, 0.85, 1.0]),
]


# ============================================================================
# Orbit Camera
# ============================================================================

class OrbitCamera:
    """Orbit camera controller for model viewing."""

    def __init__(self, base, distance=5.0, heading=30, pitch=-20):
        self.base = base
        self.distance = distance
        self.min_distance = 0.5
        self.max_distance = 50.0
        self.heading = heading
        self.pitch = pitch
        self.target = Point3(0, 0, 0)

        self.is_rotating = False
        self.is_panning = False
        self.last_mouse_pos = None

    def update_camera(self):
        """Update camera position based on orbit parameters."""
        h_rad = math.radians(self.heading)
        p_rad = math.radians(self.pitch)

        x = self.distance * math.cos(p_rad) * math.sin(h_rad)
        y = -self.distance * math.cos(p_rad) * math.cos(h_rad)
        z = self.distance * math.sin(p_rad)

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
        h_rad = math.radians(self.heading)
        right = Vec3(math.cos(h_rad), math.sin(h_rad), 0)
        up = Vec3(0, 0, 1)
        scale = self.distance * 0.002
        self.target += right * delta_x * scale
        self.target += up * delta_y * scale
        self.update_camera()

    def zoom(self, delta):
        """Zoom camera in/out."""
        self.distance *= (1.0 - delta * 0.1)
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        self.update_camera()

    def frame_model(self, bounds_min, bounds_max):
        """Auto-frame camera to fit model in view."""
        center = (bounds_min + bounds_max) * 0.5
        size = bounds_max - bounds_min
        max_dim = max(size.x, size.y, size.z)

        self.target = Point3(center.x, center.y, center.z)
        self.distance = max_dim * 2.0
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        self.heading = 30
        self.pitch = -20
        self.update_camera()


# ============================================================================
# Embedded 3D Viewer
# ============================================================================

class EmbeddedViewer(ShowBase):
    """Panda3D viewer embedded in tkinter frame."""

    def __init__(self, parent_frame):
        # Initialize without creating a window yet
        ShowBase.__init__(self, windowType='none')

        self.parent_frame = parent_frame
        self.model_np = None
        self.mesh_nodes = {}  # Maps material name to NodePath for real-time updates
        self.show_grid = True
        self.wireframe_mode = False
        self.turntable_active = False
        self.lighting_mode = 0

        # Wait for frame to be ready, then create window
        parent_frame.after(100, self._create_embedded_window)

    def _create_embedded_window(self):
        """Create the embedded Panda3D window inside tkinter frame."""
        try:
            # Get the frame's window handle
            self.parent_frame.update_idletasks()
            window_handle = self.parent_frame.winfo_id()

            # Setup window properties for embedding
            props = WindowProperties()
            props.setParentWindow(window_handle)
            props.setOrigin(0, 0)
            props.setSize(
                self.parent_frame.winfo_width(),
                self.parent_frame.winfo_height()
            )

            # Create the graphics window
            self.openDefaultWindow(props=props)

            # Configure rendering
            self.setBackgroundColor(0.25, 0.25, 0.28, 1.0)

            # Setup camera
            self.disableMouse()
            self.orbit_cam = OrbitCamera(self, distance=5.0)

            # Setup lighting
            self._setup_lighting()

            # Create grid
            self._create_grid()

            # Bind resize
            self.parent_frame.bind('<Configure>', self._on_resize)

            # Mouse bindings on the frame
            self.parent_frame.bind('<Button-1>', self._on_mouse_press_left)
            self.parent_frame.bind('<ButtonRelease-1>', self._on_mouse_release_left)
            self.parent_frame.bind('<Button-3>', self._on_mouse_press_right)
            self.parent_frame.bind('<ButtonRelease-3>', self._on_mouse_release_right)
            self.parent_frame.bind('<B1-Motion>', self._on_mouse_drag)
            self.parent_frame.bind('<B3-Motion>', self._on_mouse_drag)
            self.parent_frame.bind('<MouseWheel>', self._on_scroll_windows)
            self.parent_frame.bind('<Button-4>', self._on_scroll_up)
            self.parent_frame.bind('<Button-5>', self._on_scroll_down)

            # Update task
            self.taskMgr.add(self._update_task, 'viewer_update')

            print("3D Viewer initialized successfully")

        except Exception as e:
            print(f"Error creating embedded window: {e}")
            import traceback
            traceback.print_exc()

    def _setup_lighting(self):
        """Setup scene lighting."""
        # Ambient light
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.35, 0.35, 0.37, 1))
        self.ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(self.ambient_np)

        # Key light
        key = DirectionalLight('key')
        key.setColor(Vec4(0.9, 0.88, 0.85, 1))
        self.key_np = self.render.attachNewNode(key)
        self.key_np.setHpr(-45, -45, 0)
        self.render.setLight(self.key_np)

        # Fill light
        fill = DirectionalLight('fill')
        fill.setColor(Vec4(0.4, 0.42, 0.45, 1))
        self.fill_np = self.render.attachNewNode(fill)
        self.fill_np.setHpr(135, -30, 0)
        self.render.setLight(self.fill_np)

        # Rim light
        rim = DirectionalLight('rim')
        rim.setColor(Vec4(0.3, 0.3, 0.35, 1))
        self.rim_np = self.render.attachNewNode(rim)
        self.rim_np.setHpr(0, 45, 0)
        self.render.setLight(self.rim_np)

    def _create_grid(self):
        """Create a reference grid floor."""
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

        for i in range(-grid_size, grid_size + 1):
            y = i * grid_step
            color = axis_color_y if i == 0 else grid_color
            vertex_writer.addData3f(-grid_size * grid_step, y, 0)
            color_writer.addData4f(*color)
            vertex_writer.addData3f(grid_size * grid_step, y, 0)
            color_writer.addData4f(*color)
            lines.addVertices(vertex_idx, vertex_idx + 1)
            vertex_idx += 2

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
        """Load a GLB model and return success status."""
        if not TRIMESH_AVAILABLE:
            print("Error: trimesh not available for loading")
            return False

        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            return False

        # Remove existing model
        if self.model_np:
            self.model_np.removeNode()
            self.model_np = None
        self.mesh_nodes = {}

        try:
            # Load with trimesh
            scene = trimesh.load(filepath)

            # Create parent node for all meshes
            self.model_np = self.render.attachNewNode("model_root")

            # Collect meshes
            if isinstance(scene, trimesh.Scene):
                meshes = list(scene.geometry.items())
            else:
                meshes = [("default", scene)]

            for mesh_name, mesh in meshes:
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

                # Center vertices
                center = verts.mean(axis=0)
                verts = verts - center

                # Create Panda3D geometry
                geom_node = GeomNode(mesh_name)
                vformat = GeomVertexFormat.getV3n3()
                vdata = GeomVertexData('vertices', vformat, Geom.UHStatic)
                vdata.setNumRows(len(verts))

                vertex_writer = GeomVertexWriter(vdata, 'vertex')
                normal_writer = GeomVertexWriter(vdata, 'normal')

                for i, vert in enumerate(verts):
                    # Swap Y and Z for Panda3D coordinate system
                    vertex_writer.addData3f(float(vert[0]), float(vert[2]), float(vert[1]))
                    n = norms[i]
                    normal_writer.addData3f(float(n[0]), float(n[2]), float(n[1]))

                tris = GeomTriangles(Geom.UHStatic)
                for face in faces:
                    tris.addVertices(int(face[0]), int(face[1]), int(face[2]))
                tris.closePrimitive()

                geom = Geom(vdata)
                geom.addPrimitive(tris)
                geom_node.addGeom(geom)

                mesh_np = self.model_np.attachNewNode(geom_node)
                mesh_np.setColor(0.8, 0.8, 0.8, 1.0)

                # Store reference for material updates
                self.mesh_nodes[mesh_name] = mesh_np

            # Frame camera to model
            if self.model_np:
                bounds = self.model_np.getTightBounds()
                if bounds:
                    self.orbit_cam.frame_model(bounds[0], bounds[1])

            print(f"Model loaded: {os.path.basename(filepath)}")
            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_material_color(self, material_name: str, color: List[float]):
        """Update a material's color in real-time."""
        # For now, apply color to all mesh nodes (simplified approach)
        # In a more sophisticated implementation, we'd map GLTF materials to mesh nodes
        if self.model_np:
            r, g, b = color[0], color[1], color[2]
            a = color[3] if len(color) > 3 else 1.0

            # Apply to all meshes for now
            for np in self.mesh_nodes.values():
                np.setColor(r, g, b, a)

    def update_all_materials(self, materials: List[MaterialInfo]):
        """Update all material colors at once."""
        if not self.model_np:
            return

        # Apply average or first enabled material color to the whole model
        # This is a simplified approach; full material mapping would require
        # more complex GLTF material to mesh node mapping
        for mat in materials:
            if mat.enabled:
                r, g, b = mat.base_color[0], mat.base_color[1], mat.base_color[2]
                a = mat.base_color[3] if len(mat.base_color) > 3 else 1.0

                # Apply to all meshes
                for np in self.mesh_nodes.values():
                    np.setColor(r, g, b, a)
                break  # Use first enabled material for now

    def reset_view(self):
        """Reset camera to default view."""
        if self.model_np:
            bounds = self.model_np.getTightBounds()
            if bounds:
                self.orbit_cam.frame_model(bounds[0], bounds[1])
        else:
            self.orbit_cam.heading = 30
            self.orbit_cam.pitch = -20
            self.orbit_cam.distance = 5.0
            self.orbit_cam.target = Point3(0, 0, 0)
            self.orbit_cam.update_camera()

    def toggle_wireframe(self):
        """Toggle wireframe rendering."""
        self.wireframe_mode = not self.wireframe_mode
        if self.wireframe_mode:
            self.render.setRenderModeWireframe()
        else:
            self.render.setRenderModeFilled()
        return self.wireframe_mode

    def toggle_grid(self):
        """Toggle grid visibility."""
        self.show_grid = not self.show_grid
        if self.show_grid:
            self.grid_np.show()
        else:
            self.grid_np.hide()
        return self.show_grid

    def toggle_turntable(self):
        """Toggle auto-rotation."""
        self.turntable_active = not self.turntable_active
        return self.turntable_active

    def cycle_lighting(self):
        """Cycle through lighting presets."""
        self.lighting_mode = (self.lighting_mode + 1) % 3

        if self.lighting_mode == 0:
            self.ambient_np.node().setColor(Vec4(0.35, 0.35, 0.37, 1))
            self.key_np.node().setColor(Vec4(0.9, 0.88, 0.85, 1))
            name = "Normal"
        elif self.lighting_mode == 1:
            self.ambient_np.node().setColor(Vec4(0.5, 0.5, 0.52, 1))
            self.key_np.node().setColor(Vec4(1.2, 1.18, 1.15, 1))
            name = "Bright"
        else:
            self.ambient_np.node().setColor(Vec4(0.15, 0.15, 0.18, 1))
            self.key_np.node().setColor(Vec4(0.6, 0.58, 0.55, 1))
            name = "Dark"
        return name

    def take_screenshot(self, output_dir: str) -> Optional[str]:
        """Save screenshot and return path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)

        self.screenshot(filepath, defaultFilename=False)
        return filepath

    # === Mouse Event Handlers ===

    def _on_mouse_press_left(self, event):
        self.orbit_cam.is_rotating = True
        self.orbit_cam.last_mouse_pos = (event.x, event.y)

    def _on_mouse_release_left(self, event):
        self.orbit_cam.is_rotating = False

    def _on_mouse_press_right(self, event):
        self.orbit_cam.is_panning = True
        self.orbit_cam.last_mouse_pos = (event.x, event.y)

    def _on_mouse_release_right(self, event):
        self.orbit_cam.is_panning = False

    def _on_mouse_drag(self, event):
        if self.orbit_cam.last_mouse_pos:
            dx = event.x - self.orbit_cam.last_mouse_pos[0]
            dy = event.y - self.orbit_cam.last_mouse_pos[1]

            if self.orbit_cam.is_rotating:
                self.orbit_cam.rotate(-dx * 0.5, dy * 0.5)
            elif self.orbit_cam.is_panning:
                self.orbit_cam.pan(-dx, dy)

        self.orbit_cam.last_mouse_pos = (event.x, event.y)

    def _on_scroll_windows(self, event):
        delta = 1 if event.delta > 0 else -1
        self.orbit_cam.zoom(delta)

    def _on_scroll_up(self, event):
        self.orbit_cam.zoom(1)

    def _on_scroll_down(self, event):
        self.orbit_cam.zoom(-1)

    def _on_resize(self, event):
        """Handle window resize."""
        if hasattr(self, 'win') and self.win:
            props = WindowProperties()
            props.setSize(event.width, event.height)
            self.win.requestProperties(props)

    def _update_task(self, task):
        """Main update loop."""
        if self.turntable_active:
            self.orbit_cam.heading += 0.5
            self.orbit_cam.update_camera()
        return Task.cont


# ============================================================================
# Material Widget (Compact Version)
# ============================================================================

class CompactMaterialWidget(ttk.Frame):
    """Compact widget for editing a single material's color."""

    def __init__(self, parent, material: MaterialInfo, on_change_callback=None):
        super().__init__(parent)
        self.material = material
        self.on_change = on_change_callback

        self.r_var = tk.DoubleVar(value=material.base_color[0])
        self.g_var = tk.DoubleVar(value=material.base_color[1])
        self.b_var = tk.DoubleVar(value=material.base_color[2])
        self.enabled_var = tk.BooleanVar(value=material.enabled)

        self._create_widgets()
        self._update_preview()

    def _create_widgets(self):
        """Create the material editing widgets."""
        self.configure(relief="groove", padding=3)

        # Header: checkbox, name, preview, pick button
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 2))

        ttk.Checkbutton(
            header, variable=self.enabled_var, command=self._on_enable_toggle
        ).pack(side="left")

        ttk.Label(header, text=self.material.name, font=("TkDefaultFont", 9, "bold"),
                  width=18, anchor="w").pack(side="left", padx=3)

        self.preview_canvas = tk.Canvas(header, width=30, height=20,
                                         relief="sunken", borderwidth=1)
        self.preview_canvas.pack(side="left", padx=3)

        ttk.Button(header, text="Pick", command=self._pick_color,
                   width=5).pack(side="left", padx=2)
        ttk.Button(header, text="Reset", command=self._reset_color,
                   width=5).pack(side="left")

        # Sliders frame
        sliders = ttk.Frame(self)
        sliders.pack(fill="x", pady=2)

        for label, var, color in [("R", self.r_var, "red"),
                                   ("G", self.g_var, "green"),
                                   ("B", self.b_var, "blue")]:
            row = ttk.Frame(sliders)
            row.pack(fill="x")
            ttk.Label(row, text=label, width=2).pack(side="left")
            slider = ttk.Scale(row, from_=0.0, to=1.0, variable=var,
                              orient="horizontal",
                              command=lambda v: self._on_slider_change())
            slider.pack(side="left", fill="x", expand=True, padx=2)

        # Preset buttons
        presets = self._get_relevant_presets()
        if presets:
            preset_frame = ttk.Frame(self)
            preset_frame.pack(fill="x", pady=(2, 0))
            for preset in presets[:4]:  # Show max 4 presets
                btn = ttk.Button(preset_frame, text=preset.name,
                                command=lambda p=preset: self._apply_preset(p), width=7)
                btn.pack(side="left", padx=1)

    def _get_relevant_presets(self) -> List[ColorPreset]:
        """Get presets relevant to this material."""
        name_lower = self.material.name.lower()
        if any(x in name_lower for x in ["skin", "body", "face", "hand", "arm"]):
            return SKIN_PRESETS
        elif any(x in name_lower for x in ["hair", "head"]):
            return HAIR_PRESETS
        return CLOTHING_PRESETS

    def _on_slider_change(self):
        """Handle slider value changes."""
        r = max(0.0, min(1.0, self.r_var.get()))
        g = max(0.0, min(1.0, self.g_var.get()))
        b = max(0.0, min(1.0, self.b_var.get()))

        self.material.base_color = [r, g, b, self.material.base_color[3]]
        self._update_preview()

        if self.on_change:
            self.on_change()

    def _on_enable_toggle(self):
        """Handle enable/disable toggle."""
        self.material.enabled = self.enabled_var.get()
        if self.on_change:
            self.on_change()

    def _update_preview(self):
        """Update the color preview canvas."""
        r = int(self.r_var.get() * 255)
        g = int(self.g_var.get() * 255)
        b = int(self.b_var.get() * 255)
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.preview_canvas.delete("all")
        self.preview_canvas.create_rectangle(2, 2, 28, 18, fill=color, outline="black")

    def _pick_color(self):
        """Open color picker dialog."""
        current_rgb = (
            int(self.r_var.get() * 255),
            int(self.g_var.get() * 255),
            int(self.b_var.get() * 255)
        )
        result = colorchooser.askcolor(color=current_rgb,
                                       title=f"Choose color for {self.material.name}")
        if result[0]:
            rgb = result[0]
            self.r_var.set(round(rgb[0] / 255, 3))
            self.g_var.set(round(rgb[1] / 255, 3))
            self.b_var.set(round(rgb[2] / 255, 3))
            self._on_slider_change()

    def _reset_color(self):
        """Reset to original color."""
        orig = self.material.original_color
        self.r_var.set(orig[0])
        self.g_var.set(orig[1])
        self.b_var.set(orig[2])
        self._on_slider_change()

    def _apply_preset(self, preset: ColorPreset):
        """Apply a color preset."""
        self.r_var.set(preset.color[0])
        self.g_var.set(preset.color[1])
        self.b_var.set(preset.color[2])
        self._on_slider_change()


# ============================================================================
# Main Application
# ============================================================================

class CharacterStudioApp:
    """Main application - unified character editor with real-time 3D preview."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Character Customization Studio")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # State
        self.current_file: Optional[str] = None
        self.gltf: Optional[GLTF2] = None
        self.materials: List[MaterialInfo] = []
        self.material_widgets: List[CompactMaterialWidget] = []
        self.undo_stack: List[Dict] = []
        self.viewer: Optional[EmbeddedViewer] = None

        # Output directory
        self.output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "models", "characterdev"
        )

        self._create_ui()
        self._start_panda3d()

    def _create_ui(self):
        """Create the main UI layout."""
        # Main horizontal paned window
        self.paned = ttk.PanedWindow(self.root, orient="horizontal")
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel - Controls (~40%)
        left_frame = ttk.Frame(self.paned, width=450)
        self.paned.add(left_frame, weight=40)

        # Right panel - 3D Viewer (~60%)
        right_frame = ttk.Frame(self.paned, width=700)
        self.paned.add(right_frame, weight=60)

        # === Left Panel Contents ===
        self._create_left_panel(left_frame)

        # === Right Panel Contents ===
        self._create_right_panel(right_frame)

    def _create_left_panel(self, parent):
        """Create left panel with controls."""
        # Title
        ttk.Label(parent, text="Character Customization",
                  font=("TkDefaultFont", 14, "bold")).pack(pady=(5, 10))

        # File selection
        file_frame = ttk.LabelFrame(parent, text="GLB File", padding=5)
        file_frame.pack(fill="x", padx=5, pady=5)

        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.pack(side="left", fill="x", expand=True)

        ttk.Button(file_frame, text="Browse...",
                   command=self._browse_file).pack(side="right")

        # Status
        self.status_label = ttk.Label(parent, text="Load a GLB file to begin",
                                       foreground="gray")
        self.status_label.pack(fill="x", padx=5)

        # Materials list with scrollbar
        materials_frame = ttk.LabelFrame(parent, text="Materials", padding=5)
        materials_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Canvas for scrolling
        self.canvas = tk.Canvas(materials_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(materials_frame, orient="vertical",
                                  command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Bottom buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill="x", padx=5, pady=5)

        # Row 1: Reset/Undo
        row1 = ttk.Frame(buttons_frame)
        row1.pack(fill="x", pady=2)

        ttk.Button(row1, text="Reset All",
                   command=self._reset_all).pack(side="left", padx=2)
        ttk.Button(row1, text="Undo",
                   command=self._undo).pack(side="left", padx=2)
        ttk.Button(row1, text="Random",
                   command=self._randomize_colors).pack(side="left", padx=2)

        # Row 2: Save
        row2 = ttk.Frame(buttons_frame)
        row2.pack(fill="x", pady=2)

        ttk.Button(row2, text="Save As...",
                   command=self._save_file).pack(side="left", padx=2)
        ttk.Button(row2, text="Quick Save",
                   command=self._quick_save).pack(side="left", padx=2)

    def _create_right_panel(self, parent):
        """Create right panel with 3D viewer."""
        # Viewer title
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(title_frame, text="3D Preview",
                  font=("TkDefaultFont", 14, "bold")).pack(side="left")

        self.viewer_status = ttk.Label(title_frame, text="", foreground="gray")
        self.viewer_status.pack(side="right")

        # 3D Viewer frame (Panda3D will be embedded here)
        self.viewer_frame = tk.Frame(parent, bg="black", width=700, height=550)
        self.viewer_frame.pack(fill="both", expand=True)
        self.viewer_frame.pack_propagate(False)

        # Viewer controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill="x", pady=5)

        ttk.Button(controls_frame, text="Reset View",
                   command=self._reset_view).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="Wireframe",
                   command=self._toggle_wireframe).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="Grid",
                   command=self._toggle_grid).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="Lighting",
                   command=self._cycle_lighting).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="Rotate",
                   command=self._toggle_turntable).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="Screenshot",
                   command=self._take_screenshot).pack(side="left", padx=2)

        # Hint text
        hint = ttk.Label(controls_frame,
                         text="Left drag: Rotate | Right drag: Pan | Scroll: Zoom",
                         foreground="gray")
        hint.pack(side="right", padx=5)

    def _start_panda3d(self):
        """Start the Panda3D embedded viewer."""
        if not PANDA3D_AVAILABLE:
            self.viewer_status.config(text="Panda3D not available",
                                       foreground="red")
            return

        try:
            self.viewer = EmbeddedViewer(self.viewer_frame)
            self.viewer_status.config(text="Ready", foreground="green")

            # Start Panda3D update loop in tkinter
            self._panda_step()
        except Exception as e:
            print(f"Error starting Panda3D: {e}")
            self.viewer_status.config(text=f"Error: {e}", foreground="red")

    def _panda_step(self):
        """Step Panda3D task manager from tkinter mainloop."""
        if self.viewer:
            try:
                self.viewer.taskMgr.step()
            except Exception:
                pass
        # Schedule next step
        self.root.after(16, self._panda_step)  # ~60 FPS

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling in materials list."""
        # Only scroll if mouse is over the canvas
        widget = event.widget
        if widget == self.canvas or str(widget).startswith(str(self.canvas)):
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")

    def _browse_file(self):
        """Open file browser to select GLB file."""
        initial_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "models"
        )
        if not os.path.exists(initial_dir):
            initial_dir = os.path.dirname(os.path.abspath(__file__))

        filename = filedialog.askopenfilename(
            title="Select GLB File",
            initialdir=initial_dir,
            filetypes=[("GLB Files", "*.glb"), ("GLTF Files", "*.gltf"),
                       ("All Files", "*.*")]
        )

        if filename:
            self._load_file(filename)

    def _load_file(self, filepath: str):
        """Load a GLB file and extract materials."""
        if not PYGLTFLIB_AVAILABLE:
            messagebox.showerror("Missing Dependency",
                                "pygltflib is not installed.\n\n"
                                "Install with: pip install pygltflib")
            return

        try:
            self.gltf = GLTF2().load(filepath)
            self.current_file = filepath
            self.materials = []
            self.undo_stack = []

            # Extract materials
            if self.gltf.materials:
                for idx, mat in enumerate(self.gltf.materials):
                    name = mat.name or f"Material_{idx}"
                    base_color = [1.0, 1.0, 1.0, 1.0]
                    if mat.pbrMetallicRoughness:
                        if mat.pbrMetallicRoughness.baseColorFactor:
                            base_color = list(mat.pbrMetallicRoughness.baseColorFactor)

                    self.materials.append(MaterialInfo(
                        index=idx,
                        name=name,
                        base_color=base_color.copy(),
                        original_color=base_color.copy(),
                        enabled=True
                    ))

            # Update UI
            self.file_label.config(text=os.path.basename(filepath))
            self.status_label.config(text=f"Loaded {len(self.materials)} materials",
                                      foreground="green")

            self._rebuild_material_widgets()

            # Load in 3D viewer
            if self.viewer:
                self.viewer.load_model(filepath)
                self._update_3d_preview()

        except Exception as e:
            messagebox.showerror("Error Loading File", str(e))
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def _rebuild_material_widgets(self):
        """Rebuild all material widgets."""
        for widget in self.material_widgets:
            widget.destroy()
        self.material_widgets = []

        for material in self.materials:
            widget = CompactMaterialWidget(
                self.scrollable_frame,
                material,
                on_change_callback=self._on_material_change
            )
            widget.pack(fill="x", pady=3, padx=3)
            self.material_widgets.append(widget)

        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_material_change(self):
        """Called when any material is changed - update 3D preview."""
        self._save_undo_state()
        self._update_3d_preview()

    def _update_3d_preview(self):
        """Update the 3D preview with current material colors."""
        if self.viewer and self.materials:
            self.viewer.update_all_materials(self.materials)

    def _save_undo_state(self):
        """Save current state to undo stack."""
        state = {
            "materials": [
                {"index": m.index, "color": m.base_color.copy()}
                for m in self.materials
            ]
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def _undo(self):
        """Undo last change."""
        if len(self.undo_stack) < 2:
            return

        self.undo_stack.pop()
        state = self.undo_stack[-1]

        for mat_state in state["materials"]:
            for mat in self.materials:
                if mat.index == mat_state["index"]:
                    mat.base_color = mat_state["color"].copy()
                    break

        self._rebuild_material_widgets()
        self._update_3d_preview()
        self.status_label.config(text="Undo applied", foreground="blue")

    def _reset_all(self):
        """Reset all materials to original colors."""
        for mat in self.materials:
            mat.base_color = mat.original_color.copy()

        self._rebuild_material_widgets()
        self._update_3d_preview()
        self.status_label.config(text="All materials reset", foreground="blue")

    def _randomize_colors(self):
        """Randomize all material colors."""
        import random
        self._save_undo_state()

        for mat in self.materials:
            mat.base_color = [
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
                1.0
            ]

        self._rebuild_material_widgets()
        self._update_3d_preview()
        self.status_label.config(text="Colors randomized", foreground="purple")

    # === 3D Viewer Controls ===

    def _reset_view(self):
        """Reset 3D camera view."""
        if self.viewer:
            self.viewer.reset_view()

    def _toggle_wireframe(self):
        """Toggle wireframe mode."""
        if self.viewer:
            state = self.viewer.toggle_wireframe()
            self.status_label.config(
                text=f"Wireframe: {'ON' if state else 'OFF'}",
                foreground="blue")

    def _toggle_grid(self):
        """Toggle grid visibility."""
        if self.viewer:
            state = self.viewer.toggle_grid()
            self.status_label.config(
                text=f"Grid: {'ON' if state else 'OFF'}",
                foreground="blue")

    def _cycle_lighting(self):
        """Cycle through lighting presets."""
        if self.viewer:
            name = self.viewer.cycle_lighting()
            self.status_label.config(text=f"Lighting: {name}", foreground="blue")

    def _toggle_turntable(self):
        """Toggle auto-rotation."""
        if self.viewer:
            state = self.viewer.toggle_turntable()
            self.status_label.config(
                text=f"Turntable: {'ON' if state else 'OFF'}",
                foreground="blue")

    def _take_screenshot(self):
        """Take a screenshot."""
        if self.viewer:
            os.makedirs(self.output_dir, exist_ok=True)
            filepath = self.viewer.take_screenshot(self.output_dir)
            if filepath:
                self.status_label.config(
                    text=f"Screenshot: {os.path.basename(filepath)}",
                    foreground="green")

    # === Save Functions ===

    def _save_file(self):
        """Save modified GLB with custom name."""
        if not self.gltf or not self.current_file:
            messagebox.showwarning("No File", "Please load a file first.")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{base_name}_custom_{timestamp}.glb"

        output_path = filedialog.asksaveasfilename(
            title="Save Modified GLB",
            initialdir=self.output_dir,
            initialfile=default_name,
            defaultextension=".glb",
            filetypes=[("GLB Files", "*.glb")]
        )

        if output_path:
            self._do_save(output_path)

    def _quick_save(self):
        """Quick save with auto-generated name."""
        if not self.gltf or not self.current_file:
            messagebox.showwarning("No File", "Please load a file first.")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir,
                                   f"{base_name}_custom_{timestamp}.glb")

        self._do_save(output_path)

    def _do_save(self, output_path: str):
        """Perform the actual save operation."""
        try:
            # Apply modifications to GLTF
            for mat_info in self.materials:
                if mat_info.enabled:
                    gltf_mat = self.gltf.materials[mat_info.index]
                    if gltf_mat.pbrMetallicRoughness:
                        gltf_mat.pbrMetallicRoughness.baseColorFactor = mat_info.base_color

            # Save GLB
            self.gltf.save(output_path)

            # Save metadata
            self._save_metadata(output_path)

            # Log modification
            self._log_modification(output_path)

            self.status_label.config(text=f"Saved: {os.path.basename(output_path)}",
                                      foreground="green")
            messagebox.showinfo("Save Successful",
                               f"File saved to:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            self.status_label.config(text=f"Save failed: {e}", foreground="red")

    def _save_metadata(self, output_path: str):
        """Save metadata JSON alongside the GLB file."""
        meta_path = output_path.replace(".glb", "_meta.json")

        modifications = []
        for mat in self.materials:
            if mat.enabled:
                modifications.append({
                    "material": mat.name,
                    "original_color": mat.original_color,
                    "new_color": mat.base_color
                })

        metadata = {
            "source_file": os.path.basename(self.current_file),
            "output_file": os.path.basename(output_path),
            "timestamp": datetime.now().isoformat(),
            "modifications": modifications,
            "notes": ""
        }

        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _log_modification(self, output_path: str):
        """Append to modification history log."""
        log_path = os.path.join(self.output_dir, "modifications.txt")

        entry = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{os.path.basename(self.current_file)} -> "
            f"{os.path.basename(output_path)}\n"
        )

        with open(log_path, "a") as f:
            f.write(entry)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point."""
    # Check dependencies
    missing = []
    if not PYGLTFLIB_AVAILABLE:
        missing.append("pygltflib")
    if not PANDA3D_AVAILABLE:
        missing.append("panda3d")
    if not TRIMESH_AVAILABLE:
        missing.append("trimesh")

    if missing:
        print("=" * 60)
        print("Missing dependencies:", ", ".join(missing))
        print("Install with: pip install", " ".join(missing))
        print("=" * 60)

    root = tk.Tk()
    app = CharacterStudioApp(root)

    # Handle window close
    def on_close():
        if app.viewer:
            try:
                app.viewer.destroy()
            except Exception:
                pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


if __name__ == "__main__":
    main()
