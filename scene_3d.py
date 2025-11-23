#!/usr/bin/env python3
"""
3D Scene for Pemberton Manor Mystery.
Creates Victorian library environment with table and 4 suspect characters.
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    WindowProperties, AmbientLight, DirectionalLight, PointLight,
    CardMaker, Vec3, Point3, NodePath, Texture, TransparencyAttrib,
    GeomNode, Geom, GeomVertexData, GeomVertexFormat,
    GeomTriangles, GeomVertexWriter
)
from direct.interval.LerpInterval import LerpHprInterval
import math
import os


# Character configuration
CHARACTER_CONFIG = {
    'major': {
        'name': 'Major Thornton',
        'model': 'assets/models/old_female.glb',
        'color': (0.55, 0.35, 0.20, 1.0),  # Brown
        'position': (-2.5, 1, 0),  # Front-left (closer to camera)
        'heading': 0,
    },
    'lady': {
        'name': 'Lady Ashworth',
        'model': 'assets/models/old_female.glb',
        'color': (0.58, 0.34, 0.65, 1.0),  # Purple
        'position': (2.5, 1, 0),  # Front-right (closer to camera)
        'heading': 0,
    },
    'maid': {
        'name': 'Clara Finch',
        'model': 'assets/models/Anime_School_Teacher.GLB',
        'color': (0.39, 0.58, 0.78, 1.0),  # Blue
        'position': (-2.5, 3, 0),  # Back-left (farther)
        'heading': 0,
    },
    'student': {
        'name': 'Thomas Whitmore',
        'model': 'assets/models/Anime_School_Teacher.GLB',
        'color': (0.30, 0.60, 0.39, 1.0),  # Green
        'position': (2.5, 3, 0),  # Back-right (farther)
        'heading': 0,
    },
}


class Scene3D:
    """3D Victorian library scene with table and characters."""

    def __init__(self, base: ShowBase):
        """
        Initialize the 3D scene.

        Args:
            base: The ShowBase instance (Panda3D application)
        """
        self.base = base
        self.characters = {}  # Store character NodePaths
        self.focused_character = None
        self._camera_interval = None

        self._setup_background()
        self._create_table()
        self._load_characters()
        self._setup_lighting()
        self._setup_camera()

    def _setup_background(self):
        """Load library background as backdrop."""
        bg_path = 'assets/backgrounds/library.jpg'

        # Create a large card for the background
        card = CardMaker('background')
        card.setFrame(-20, 20, -10, 10)

        self.background = self.base.render.attachNewNode(card.generate())
        self.background.setPos(0, 20, 0)  # Far back
        self.background.setTwoSided(True)

        # Load and apply texture if available
        if os.path.exists(bg_path):
            tex = self.base.loader.loadTexture(bg_path)
            self.background.setTexture(tex)
            print(f"✓ Background loaded: {bg_path}")
        else:
            # Fallback: solid color
            self.background.setColor(0.2, 0.15, 0.1, 1)
            print(f"⚠ Background not found, using fallback color")

    def _create_table(self):
        """Create table geometry - a rectangular table in the center."""
        # Table top - create using CardMaker for simplicity
        table_card = CardMaker('table_top')
        table_card.setFrame(-1.5, 1.5, -1, 1)

        self.table = self.base.render.attachNewNode(table_card.generate())
        self.table.setPos(0, 0, 0)
        self.table.setP(-90)  # Rotate to be horizontal
        self.table.setColor(0.4, 0.25, 0.15, 1)  # Dark wood color

        # Table edge/border
        edge_card = CardMaker('table_edge')
        edge_card.setFrame(-1.55, 1.55, -0.1, 0)

        # Front edge
        front_edge = self.base.render.attachNewNode(edge_card.generate())
        front_edge.setPos(0, -1, 0)
        front_edge.setColor(0.3, 0.18, 0.1, 1)

        # Back edge
        back_edge = self.base.render.attachNewNode(edge_card.generate())
        back_edge.setPos(0, 1, 0)
        back_edge.setH(180)
        back_edge.setColor(0.3, 0.18, 0.1, 1)

        print("✓ Table created")

    def _load_model_with_trimesh(self, model_path):
        """Load GLB using trimesh and convert to Panda3D geometry."""
        try:
            import trimesh
            import numpy as np
        except ImportError:
            print("  trimesh not installed, using placeholder")
            return None

        try:
            # Load with trimesh
            scene = trimesh.load(model_path)
            print(f"  Loaded with trimesh: {type(scene)}")

            # Collect all valid meshes
            all_vertices = []
            all_normals = []
            all_faces = []
            vertex_offset = 0

            # Get meshes from scene
            if isinstance(scene, trimesh.Scene):
                meshes = list(scene.geometry.values())
                print(f"  Scene has {len(meshes)} geometry objects")
            else:
                meshes = [scene]

            for mesh_idx, mesh in enumerate(meshes):
                # Skip non-mesh objects (like PointCloud, Path, etc.)
                if not hasattr(mesh, 'vertices') or not hasattr(mesh, 'faces'):
                    print(f"    Mesh {mesh_idx}: skipping (no vertices/faces)")
                    continue

                verts = np.array(mesh.vertices)
                faces = np.array(mesh.faces)

                if len(verts) == 0 or len(faces) == 0:
                    print(f"    Mesh {mesh_idx}: empty")
                    continue

                # Check for invalid values
                if np.any(~np.isfinite(verts)):
                    print(f"    Mesh {mesh_idx}: has inf/nan vertices, skipping")
                    continue

                print(f"    Mesh {mesh_idx}: {len(verts)} verts, {len(faces)} faces, bounds: {verts.min(axis=0)} to {verts.max(axis=0)}")

                # Get normals
                if hasattr(mesh, 'vertex_normals') and mesh.vertex_normals is not None:
                    norms = np.array(mesh.vertex_normals)
                else:
                    norms = np.zeros_like(verts)
                    norms[:, 2] = 1.0

                # Offset faces for concatenation
                offset_faces = faces + vertex_offset

                all_vertices.append(verts)
                all_normals.append(norms)
                all_faces.append(offset_faces)
                vertex_offset += len(verts)

            if not all_vertices:
                print("  ERROR: No valid meshes found")
                return None

            # Concatenate all meshes
            vertices = np.vstack(all_vertices)
            normals = np.vstack(all_normals)
            faces = np.vstack(all_faces)

            print(f"  Combined: {len(vertices)} verts, {len(faces)} faces")
            print(f"  Bounds: {vertices.min(axis=0)} to {vertices.max(axis=0)}")

            # Center at origin
            center = vertices.mean(axis=0)
            vertices = vertices - center

            # Create Panda3D GeomNode
            geom_node = GeomNode('model')

            # Create vertex data
            vformat = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData('vertices', vformat, Geom.UHStatic)
            vdata.setNumRows(len(vertices))

            vertex_writer = GeomVertexWriter(vdata, 'vertex')
            normal_writer = GeomVertexWriter(vdata, 'normal')

            for i, vert in enumerate(vertices):
                # Swap Y and Z for Panda3D (GLB Z-up -> Panda3D Y-forward)
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

            node_path = NodePath(geom_node)
            print(f"  ✓ Created Panda3D node with {len(vertices)} vertices")

            return node_path

        except Exception as e:
            import traceback
            print(f"  Error loading with trimesh: {e}")
            traceback.print_exc()
            return None

    def _load_characters(self):
        """Load 4 character models with positions and colors."""
        for char_id, config in CHARACTER_CONFIG.items():
            model_path = config['model']
            pos = config['position']

            char_node = None

            if os.path.exists(model_path):
                print(f"Loading {config['name']} from {model_path}...")

                # Try trimesh loader first (bypasses Panda3D's broken GLB support)
                char_node = self._load_model_with_trimesh(model_path)

                if char_node:
                    # FIX: Rotate to stand upright BEFORE attaching to scene
                    char_node.setP(-90)  # Pitch -90 to stand vertical

                    char_node.reparentTo(self.base.render)

                    # Position character
                    char_node.setPos(pos[0], pos[1], 0)

                    # Scale larger for visibility
                    char_node.setScale(2.5)

                    # Apply color tint
                    char_node.setColor(*config['color'])

                    print(f"✓ Loaded {config['name']} with trimesh")
                else:
                    print(f"  Trimesh failed, using placeholder")

            if char_node is None:
                # Fallback: create VISIBLE placeholder geometry
                char_node = self._create_placeholder_character()
                char_node.reparentTo(self.base.render)
                char_node.setPos(pos[0], pos[1], 0)
                char_node.setH(config['heading'])
                char_node.setColor(*config['color'])
                print(f"⚠ Using placeholder for {config['name']} at {pos}")

            self.characters[char_id] = char_node

        print(f"✓ Loaded {len(self.characters)} characters")

    def _create_placeholder_character(self):
        """Create a visible placeholder for missing character models."""
        from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, GeomTriangles, GeomVertexWriter, GeomNode

        # Create a simple 3D box as placeholder (more visible than a card)
        card = CardMaker('placeholder')
        card.setFrame(-0.4, 0.4, 0, 1.8)  # Wider and taller
        node = NodePath(card.generate())

        # Make it double-sided so visible from all angles
        node.setTwoSided(True)

        return node

    def _setup_lighting(self):
        """Set up Victorian-style warm lighting."""
        # Ambient light - dim base lighting
        ambient = AmbientLight('ambient')
        ambient.setColor((0.3, 0.25, 0.2, 1))  # Warm dim
        ambient_np = self.base.render.attachNewNode(ambient)
        self.base.render.setLight(ambient_np)

        # Main directional light - simulating window light
        sun = DirectionalLight('sun')
        sun.setColor((0.7, 0.6, 0.5, 1))  # Warm sunlight
        sun_np = self.base.render.attachNewNode(sun)
        sun_np.setHpr(-30, -60, 0)
        self.base.render.setLight(sun_np)

        # Point light - simulating oil lamp on table
        lamp = PointLight('lamp')
        lamp.setColor((0.8, 0.6, 0.3, 1))  # Warm orange
        lamp.setAttenuation((1, 0, 0.1))
        lamp_np = self.base.render.attachNewNode(lamp)
        lamp_np.setPos(0, 0, 1)  # Above table
        self.base.render.setLight(lamp_np)

        print("✓ Victorian lighting configured")

    def _setup_camera(self):
        """Position camera at detective's seat."""
        self.base.disableMouse()

        # Detective POV - seated at table, slightly elevated
        self.base.camera.setPos(0, -4, 1.5)
        self.base.camera.lookAt(0, 0, 0.5)

        print("✓ Camera positioned at detective seat")

    def focus_character(self, character_id: str, duration: float = 0.8):
        """Smoothly rotate camera to face character."""
        if character_id not in self.characters:
            print(f"Warning: Unknown character {character_id}")
            return

        # Stop any existing animation
        if self._camera_interval:
            self._camera_interval.finish()

        # FIX 2: Use fixed heading angles (small rotations from forward)
        angle_map = {
            'major': -30,    # Front-left: 30° left
            'lady': 30,      # Front-right: 30° right
            'maid': -20,     # Back-left: 20° left
            'student': 20,   # Back-right: 20° right
        }

        target_heading = angle_map.get(character_id, 0)

        # Get current camera angles
        current_hpr = self.base.camera.getHpr()
        target_hpr = Vec3(target_heading, current_hpr.getY(), 0)

        # Create smooth rotation
        self._camera_interval = LerpHprInterval(
            self.base.camera,
            duration=duration,
            hpr=target_hpr,
            blendType='easeInOut'
        )
        self._camera_interval.start()

        self.focused_character = character_id
        print(f"→ Camera focusing on {character_id} (heading: {target_heading}°)")

    def reset_camera(self, duration: float = 0.8):
        """Reset camera to neutral forward-facing position."""
        if self._camera_interval:
            self._camera_interval.finish()

        # Neutral position - looking at center of table
        neutral_hpr = Vec3(0, -10, 0)

        self._camera_interval = LerpHprInterval(
            self.base.camera,
            duration=duration,
            hpr=neutral_hpr,
            blendType='easeInOut'
        )
        self._camera_interval.start()

        self.focused_character = None
        print("→ Camera reset to neutral")

    def get_character_name(self, character_id: str) -> str:
        """Get the display name for a character."""
        if character_id in CHARACTER_CONFIG:
            return CHARACTER_CONFIG[character_id]['name']
        return character_id
