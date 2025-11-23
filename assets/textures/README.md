# Face Textures for 3D Characters

This folder contains face texture maps to apply portrait photos to 3D character faces.

## Required Textures

| Filename | Character | Description |
|----------|-----------|-------------|
| `major_face.jpg` | Major Thornton | Face texture for 3D model |
| `lady_face.jpg` | Lady Ashworth | Face texture for 3D model |
| `clara_face.jpg` | Clara Finch | Face texture for 3D model |
| `thomas_face.jpg` | Thomas Whitmore | Face texture for 3D model |

## Creating Face Textures

### From Portrait Photos

1. Take the portrait photo from `assets/portraits/`
2. Crop to face area only
3. Resize to 512x512 or 1024x1024
4. Apply to character model's face UV map in Blender

### UV Mapping Process

1. Import character model into Blender
2. Select face geometry
3. UV unwrap the face
4. Apply texture to face material
5. Export model with embedded texture (GLB)

## Alternative: Procedural Faces

If no face textures are available, the 3D models will use:
- Default material colors based on character
- Simple shading without photo-realistic faces

The 2.5D mode uses portrait images directly and doesn't require these textures.
