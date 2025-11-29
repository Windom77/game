# Interaction Test

A minimal testing environment for character interaction mechanics in isolation.

## Overview

This subproject provides a clean, simple testbed for developing and testing character interaction mechanics without the complexity of the full murder mystery game. It features:

- **Simple 3D Scene**: White/featureless environment with a single character model
- **Face-on Camera**: Natural portrait view positioned at eye level for conversation
- **Mouth Animation**: Procedural jaw/mouth animation during character speech
- **LLM Integration**: Full support for multiple LLM providers
- **Text-based UI**: DirectGUI-based interface for conversations
- **Isolated Testing**: No game logic, clues, or victory conditions

## Purpose

Use this environment to:
- Test LLM provider integrations
- Develop conversation mechanics
- Experiment with character personalities
- Debug interaction issues in isolation
- Prototype new features before adding to main game

## Project Structure

```
interaction_test/
├── main.py                      # Entry point with argument parsing
├── test_scene.py                # Minimal Panda3D scene (white environment)
├── test_character.py            # Simple Character definition
├── interaction_controller.py    # Input handling and dialogue UI
├── mouth_animation.py           # Procedural mouth/jaw animation system
└── README.md                    # This file
```

## Dependencies

Required packages:
- `panda3d` - 3D rendering engine

**Required** (for GLB model loading):
- `panda3d-gltf` - GLB/GLTF model support for Panda3D (now required for proper model loading)

Optional (for API providers):
- `requests` - HTTP requests for LLM APIs

Install with:
```bash
# Full installation (recommended)
cd ..
pip install -r requirements.txt
```

This will install all dependencies including:
- `panda3d` - 3D rendering engine
- `panda3d-gltf` - GLB/GLTF model support
- `requests` - HTTP requests for LLM APIs

**Note**: The application uses panda3d-gltf for robust GLB loading with comprehensive validation. If the GLB file cannot be loaded, it will fall back to a built-in model.

## Usage

### Basic Usage (Mock LLM)

Run with mock responses (no API required):
```bash
cd interaction_test
python main.py
```

Or:
```bash
python main.py --provider mock
```

### With Ollama (Local LLM)

1. Install and start Ollama: https://ollama.ai/
2. Pull a model: `ollama pull mistral`
3. Run the test:
```bash
python main.py --provider ollama
```

### With OpenAI

1. Set API key: `export OPENAI_API_KEY=your_key_here`
2. Run:
```bash
python main.py --provider openai
```

### With Groq

1. Get free API key: https://console.groq.com/
2. Set API key: `export GROQ_API_KEY=your_key_here`
3. Run:
```bash
python main.py --provider groq
```

### With Anthropic (Claude)

1. Set API key: `export ANTHROPIC_API_KEY=your_key_here`
2. Run:
```bash
python main.py --provider anthropic
```

## Controls

- **Type and press Enter**: Send message to character
- **ESC**: Quit application

## Character Model

The test loads `RPmeAvatar.glb` from `../assets/models/`. This is a Ready Player Me avatar that has been verified to work correctly with Panda3D's GLB loader. If the model is not found, a simple placeholder geometry will be used instead.

**Model Specifications:**
- **Type**: Ready Player Me avatar
- **Dimensions**: 0.93m × 0.33m × 1.77m (W × D × H)
- **Features**: Proper materials, textures, and facial bones included
- **Status**: ✓ Verified working

**Note**: The original `Anime_School_Teacher.glb` file has corrupted skeletal data (singular bone matrices) causing infinite bounding boxes. Ready Player Me models are standardized and work reliably.

## Features

### Face-on Camera View

The camera is positioned for a natural conversation view:
- **Position**: 2 meters in front of character at eye level (1.6m height)
- **Framing**: Head and shoulders portrait view (60-70% of frame)
- **Angle**: Slight downward tilt (5 degrees) for natural framing
- **Result**: Similar to video call framing for immersive conversation

### Procedural Mouth Animation

The mouth animation system automatically animates the character during speech:

**Animation Modes**:
1. **Jaw Animation** (preferred): Rotates jaw bone 5-15 degrees with random timing
2. **Head Bobbing** (fallback): Subtle head movements if no jaw bone found
3. **No Animation**: If no suitable bones are found in the model

**Behavior**:
- Starts when LLM response is received
- Duration based on response length (~0.05s per character)
- Random timing variations (0.1-0.2s intervals) for natural appearance
- Automatically stops when speech finishes

**Supported Bone Names**: jaw, Jaw, jawbone, mouth, mouth_bone, lower_jaw (or head/neck for fallback)

## Customization

### Change Character Personality

Edit `test_character.py` and modify the `system_prompt` in `get_test_character()`:

```python
system_prompt="You are a friendly teacher who answers questions clearly and helpfully. "
              "Keep responses concise (2-3 sentences maximum). "
              "Be warm, encouraging, and educational in your tone."
```

### Change Scene

Edit `test_scene.py` to modify:
- Background color (currently white)
- Ground plane appearance
- Lighting setup
- Camera position

### Change UI

Edit `interaction_controller.py` to modify:
- Text colors and sizes
- Input box position
- Response display format
- Conversation history length

## Technical Notes

### LLM Interface Integration

This subproject reuses the parent directory's `llm_interface.py` module, which provides:
- `LLMProvider` abstract base class
- `ConversationHistory` for maintaining context
- `get_provider()` factory function
- Support for multiple providers

### Robust GLB Loading

Character models are loaded using **panda3d-gltf** with comprehensive validation:

**Loading Process:**
1. Configures Panda3D with PRC settings for panda3d-gltf support
2. Enables verbose Assimp logging for debugging
3. Loads the GLB file using `loader.loadModel()`
4. Validates the loaded model (geometry, bounds, materials)
5. Auto-scales to 2.0m height with uniform scaling
6. Auto-positions camera based on bounding box

**Model Validation:**
The system validates loaded models by checking:
- GeomNode count (must have geometry)
- Vertex count (must have vertices)
- Triangle count
- Bounding box (must be non-degenerate)
- Material and texture counts

**Debug Output:**
When loading a model, comprehensive debug information is printed:
- Full file path and size
- Model loading status
- Vertex and triangle counts
- Bounding box dimensions
- Material/texture counts
- Camera auto-positioning calculations

**Auto Camera Positioning:**
The camera distance is automatically calculated based on the model's bounding box:
- Uses field of view (45 degrees) to calculate optimal distance
- Adds 20% margin for comfortable framing
- Positions camera at model center height
- Ensures entire model is visible in frame

### Error Handling

The application includes error handling for:
- Missing dependencies
- Missing character model files
- Panda3D initialization failures
- LLM API failures (displays error messages in UI)

## Differences from Main Game

This test environment intentionally omits:
- Multiple characters
- Game state/logic
- Clue system
- Victory conditions
- Victorian murder mystery theme
- Complex scene backgrounds
- Character selection UI

## Independent Operation

This subproject is completely independent from the main game and can be:
- Moved to a different directory
- Shared separately
- Modified without affecting the main game
- Used as a template for other testing environments

## Troubleshooting

### "Panda3D is not installed"
```bash
pip install panda3d
```

### "trimesh not installed"
The application will use placeholder geometry if trimesh is missing. For full functionality:
```bash
pip install trimesh numpy
```

### "Provider not available"
For API providers:
- Check that your API key environment variable is set
- Verify you have the `requests` library installed
- For Ollama, ensure the service is running: `ollama serve`

The application will automatically fall back to mock provider if the requested provider is unavailable.

### Model doesn't appear
- Check that `../assets/models/Anime_School_Teacher.glb` exists
- If missing, the app will use a simple placeholder geometry
- The scene is intentionally minimalist (white background)

## Future Enhancements

Potential additions for this test environment:
- Multiple test characters
- Camera controls (orbit, zoom)
- Different scene presets
- Conversation history export
- Performance metrics
- Voice input/output testing
