# Character Development Directory

This folder contains customized character models created with the **Character Customization Tools**.

## Available Tools

| Tool | Description | Best For |
|------|-------------|----------|
| `character_editor.py` | GUI color editor with presets | Editing material colors |
| `model_viewer.py` | Standalone 3D viewer | Previewing/comparing models |
| **Blender** | Full 3D editor (external) | Complex edits, best results |

---

## Recommended Workflow

For best results, use **Blender** (free, professional):

1. **Import**: File → Import → glTF 2.0 (.glb)
2. **Edit**: Select mesh, go to Material Properties, adjust Base Color
3. **Export**: File → Export → glTF 2.0 (.glb)

For quick color tweaks, use the built-in tools below.

---

## Character Editor

GUI tool for editing GLB material colors.

### Running the Editor

```bash
# From the game directory
python character_editor.py
```

### Basic Workflow

1. **Load a Model**: Click "Browse..." and select a GLB file from `assets/models/`
2. **Edit Colors**: Use the sliders or color picker to modify material colors
3. **Preview**: Each material shows a colored preview square
4. **Save**: Click "Save As..." to export the modified model

### Quick Reference

| Action | How To |
|--------|--------|
| Load file | Browse... button |
| Change color | Drag RGB sliders or click "Pick Color..." |
| Apply preset | Click preset buttons (Pale, Tan, etc.) |
| Reset one material | Click "Reset" on that material |
| Reset all materials | Click "Reset All" |
| Undo last change | Click "Undo" |
| Quick save | Click "Quick Save" (auto-names file) |

---

## Color Presets Reference

### Skin Tones

| Preset | RGB Values | Description |
|--------|------------|-------------|
| Pale | 0.95, 0.87, 0.82 | Very light, European |
| Fair | 0.92, 0.78, 0.68 | Light with warm undertones |
| Medium | 0.82, 0.64, 0.52 | Mediterranean/Latin |
| Tan | 0.76, 0.57, 0.45 | Sun-kissed |
| Brown | 0.55, 0.38, 0.28 | South Asian/Middle Eastern |
| Dark | 0.36, 0.24, 0.18 | African/Deep brown |

### Hair Colors

| Preset | RGB Values | Description |
|--------|------------|-------------|
| Black | 0.05, 0.05, 0.05 | Jet black |
| Dark Brown | 0.20, 0.12, 0.08 | Nearly black |
| Brown | 0.35, 0.22, 0.15 | Medium brown |
| Auburn | 0.50, 0.25, 0.15 | Reddish-brown |
| Blonde | 0.85, 0.70, 0.45 | Golden blonde |
| Red | 0.60, 0.20, 0.10 | Ginger/Red |
| Gray | 0.60, 0.60, 0.60 | Silver/Gray |
| White | 0.95, 0.95, 0.95 | Elderly/Platinum |

### Victorian Clothing Colors

| Preset | RGB Values | Description |
|--------|------------|-------------|
| Black | 0.08, 0.08, 0.08 | Formal/Mourning |
| White | 0.95, 0.95, 0.95 | Servant aprons |
| Navy | 0.10, 0.15, 0.30 | Military/Formal |
| Burgundy | 0.45, 0.10, 0.15 | Rich Victorian red |
| Forest Green | 0.15, 0.30, 0.15 | Hunting attire |
| Victorian Purple | 0.35, 0.20, 0.40 | Nobility |
| Maid Gray | 0.40, 0.40, 0.42 | Servant dress |
| Cream | 0.95, 0.92, 0.85 | Undergarments/Lace |

---

## Common Material Names

When editing GLB files, materials often have these names:

### Anime_School_Teacher.GLB
- `Body` / `Skin` - Skin color
- `Hair` - Hair color
- `Eyes` - Eye color
- `Clothes` / `Uniform` - Clothing

### old_female.glb
- `Skin` - Face and exposed skin
- `Hair` - Hair and eyebrows
- `Dress` - Main clothing
- `Accessories` - Jewelry, buttons

---

## File Naming Convention

Saved files follow this format:
```
{original_name}_custom_{YYYYMMDD}_{HHMMSS}.glb
```

Example:
```
Anime_School_Teacher_custom_20250119_143022.glb
```

---

## Output Files

Each save creates two files:

1. **GLB File**: The modified 3D model
   - `teacher_tan.glb`

2. **Metadata JSON**: Record of changes made
   - `teacher_tan_meta.json`

### Metadata JSON Format

```json
{
  "source_file": "Anime_School_Teacher.GLB",
  "output_file": "teacher_tan.glb",
  "timestamp": "2025-01-19T14:30:22",
  "modifications": [
    {
      "material": "Body",
      "original_color": [1.0, 0.9, 0.85, 1.0],
      "new_color": [0.76, 0.57, 0.45, 1.0]
    }
  ],
  "notes": ""
}
```

---

## Modification Log

All saves are logged to `modifications.txt`:

```
[2025-01-19 14:30:22] Anime_School_Teacher.GLB -> teacher_tan.glb
[2025-01-19 15:45:10] old_female.glb -> lady_pale.glb
```

---

## Troubleshooting

### "pygltflib not installed"
```bash
pip install pygltflib
```

### Materials not appearing
- Some GLB files may have materials without `baseColorFactor`
- The tool will show them with default white color
- Any changes you make will be saved

### Colors look different in game
- The editor shows sRGB colors
- The game's lighting affects final appearance
- Test in-game after saving

### File won't load
- Ensure it's a valid GLB/GLTF file
- Check file isn't corrupted
- Try re-exporting from original source

---

## Tips for Victorian Characters

### Maid (Clara)
- Skin: Fair to Medium
- Hair: Brown or Auburn
- Dress: Maid Gray or Black
- Apron: White or Cream

### Lady (Ashworth)
- Skin: Pale or Fair
- Hair: Dark Brown or Auburn
- Dress: Victorian Purple or Burgundy

### Major (Thornton)
- Skin: Medium to Tan
- Hair: Gray or Dark Brown
- Uniform: Navy or Black

### Student (Thomas)
- Skin: Fair
- Hair: Brown or Blonde
- Suit: Navy or Black
