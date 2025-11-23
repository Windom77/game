# 3D Models for Phase 2.0

This folder contains 3D models for the full Panda3D rendering mode.

## Required Models

| Filename | Description | Format |
|----------|-------------|--------|
| `room.glb` | Victorian drawing room with table and chairs | GLB/GLTF |
| `major.glb` | Major Thornton (seated pose) | GLB/GLTF |
| `lady.glb` | Lady Ashworth (seated pose) | GLB/GLTF |
| `clara.glb` | Clara Finch (seated pose) | GLB/GLTF |
| `thomas.glb` | Thomas Whitmore (seated pose) | GLB/GLTF |

## Sourcing Models

### Room Model
Search Sketchfab for free Victorian interior models:
- "Victorian drawing room"
- "Victorian study interior"
- "19th century library"

Download as GLB format (GLTF Binary).

### Character Models

**Option 1: MakeHuman (Recommended)**
1. Download MakeHuman: http://www.makehumancommunity.org/
2. Create characters matching descriptions in PHASE2_DESIGN.md
3. Apply seated pose
4. Export as FBX
5. Convert to GLB using Blender

**Option 2: Mixamo**
1. Select base character from Adobe Mixamo
2. Download without animation
3. Import into Blender
4. Pose to seated position
5. Export as GLB

## Model Specifications

- **Polygon Count**: < 10,000 triangles per character
- **Scale**: 1 unit = 1 meter
- **Orientation**: Y-up, facing +Y direction
- **Texture Size**: 1024x1024 max

## Testing Models

Run with full 3D mode:
```bash
python main.py --ui 3d
```

If models are missing, the game falls back to 2.5D mode automatically.
