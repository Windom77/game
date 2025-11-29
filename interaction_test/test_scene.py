"""
Minimal 3D scene for testing character interactions.
Creates a white/featureless environment with a single character model.
"""
import os
from typing import Optional

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight, DirectionalLight, CardMaker,
    Vec3, NodePath, loadPrcFileData
)


class TestScene:
    """Minimal 3D scene for interaction testing."""

    def __init__(self, base: ShowBase, model_path: str, wireframe: bool = False):
        """
        Initialize the test scene.

        Args:
            base: The ShowBase instance (Panda3D application)
            model_path: Path to the GLB character model
            wireframe: Enable wireframe rendering for debugging (default: False)
        """
        self.base = base
        self.character_node: Optional[NodePath] = None
        self.ambient_light_np: Optional[NodePath] = None
        self.directional_light_np: Optional[NodePath] = None
        self.wireframe = wireframe

        # Configure panda3d-gltf
        loadPrcFileData("", "load-file-type p3assimp")

        self._setup_environment()
        self._create_ground_plane()
        self._setup_lighting()
        self._load_character(model_path)
        self._setup_camera()

        if self.wireframe:
            self._enable_wireframe()

    def _setup_environment(self) -> None:
        """Set up white/featureless environment."""
        self.base.setBackgroundColor(1.0, 1.0, 1.0, 1.0)
        print("✓ Environment configured (white background)")

    def _create_ground_plane(self) -> None:
        """Create a simple light gray ground plane."""
        ground_card = CardMaker('ground')
        ground_card.setFrame(-10, 10, -10, 10)

        self.ground = self.base.render.attachNewNode(ground_card.generate())
        self.ground.setPos(0, 0, 0)
        self.ground.setP(-90)  # Rotate to be horizontal
        self.ground.setColor(0.9, 0.9, 0.9, 1.0)  # Light gray

        print("✓ Ground plane created")

    def _load_character(self, model_path: str) -> None:
        """
        Load the character model - MINIMAL VERSION.

        Args:
            model_path: Path to the GLB model file
        """
        if not os.path.exists(model_path):
            print(f"⚠ Model not found: {model_path}")
            self._use_fallback_model()
            return

        print(f"Loading character model from {model_path}...")

        try:
            # Simple load - let Panda3D handle everything
            self.character_node = self.base.loader.loadModel(model_path)

            if self.character_node and not self.character_node.isEmpty():
                # Just attach to render - NO transforms
                self.character_node.reparentTo(self.base.render)

                # Reset any vertex colors that might be causing red/orange tint
                self.character_node.setColorScale(1, 1, 1, 1)

                # Apply lights
                if self.ambient_light_np:
                    self.character_node.setLight(self.ambient_light_np)
                if self.directional_light_np:
                    self.character_node.setLight(self.directional_light_np)

                print("✓ Character model loaded")

                # Debug info
                bounds = self.character_node.getTightBounds()
                if bounds:
                    min_pt, max_pt = bounds
                    print(f"  Model bounds: min={min_pt}, max={max_pt}")
                    print(f"  Height: {max_pt.z - min_pt.z:.3f}")

                return

        except Exception as e:
            print(f"⚠ Error loading model: {e}")

        # Fallback
        self._use_fallback_model()

    def _use_fallback_model(self) -> None:
        """Use a fallback model when GLB loading fails."""
        print("  Using built-in smiley model as fallback...")
        try:
            self.character_node = self.base.loader.loadModel("models/smiley")
            if self.character_node and not self.character_node.isEmpty():
                self.character_node.reparentTo(self.base.render)
                self.character_node.setPos(0, 0, 1.0)
                self.character_node.setScale(0.5)
                print("✓ Using built-in smiley model")
        except Exception as e:
            print(f"⚠ Fallback also failed: {e}")

    def _setup_lighting(self) -> None:
        """Set up basic directional lighting."""
        # Ambient light
        ambient = AmbientLight('ambient')
        ambient.setColor((0.6, 0.6, 0.6, 1.0))
        self.ambient_light_np = self.base.render.attachNewNode(ambient)
        self.base.render.setLight(self.ambient_light_np)

        # Directional light
        directional = DirectionalLight('directional')
        directional.setColor((0.8, 0.8, 0.8, 1.0))
        self.directional_light_np = self.base.render.attachNewNode(directional)
        self.directional_light_np.setHpr(-45, -45, 0)
        self.base.render.setLight(self.directional_light_np)

        print("✓ Lighting configured")

    def _setup_camera(self) -> None:
        """Position camera for front view of character (full body visible)."""
        self.base.disableMouse()

        # CAMERA POSITIONING - Front view showing full figure
        # Panda3D: +Y is forward, +Z is up, +X is right
        # Camera looks down -Y axis by default

        # old_female.glb is ~1.635 units tall, so position camera to show full figure
        # Move further back to include head and feet
        self.base.camera.setPos(0, -5.0, 0.8)  # 5 units back, at mid-height
        self.base.camera.setHpr(0, 0, 0)  # Face forward

        # Look at center of figure (mid-height)
        self.base.camera.lookAt(0, 0, 0.8)  # Center of ~1.6 unit tall figure

        print("✓ Camera positioned (full body view)")
        print(f"  Camera pos: {self.base.camera.getPos()}")
        print(f"  Camera HPR: {self.base.camera.getHpr()}")

    def _enable_wireframe(self) -> None:
        """Enable wireframe rendering for debugging."""
        self.base.render.setRenderModeWireframe()
        print("✓ Wireframe mode enabled")
