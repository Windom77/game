# Victorian Drawing Room Murder Mystery - Game Prototype

A prototype interactive RPG game featuring an LLM-powered murder mystery set in Victorian England. The player takes the role of a detective questioning four suspects around a drawing room table to uncover the murderer.

## Game Concept

- **Setting**: Victorian England, a grand drawing room
- **Duration**: ~5 minutes of interactive gameplay
- **Mechanic**: Conversational investigation - player types questions, NPCs respond in character
- **Objective**: Determine which of the four suspects committed the murder

### Characters

1. **Major Reginald Blackwood** - Retired Army Major, served in the Crimean War. Gruff, direct, speaks with military precision. Harbors secrets from the war.

2. **Lady Cordelia Ashworth** - Socialite of formerly good standing. Her family has fallen on hard times. Maintains appearances at all costs. Proud but desperate.

3. **Molly Finch** - Young maid, assistant to Lady Ashworth. Working class, nervous around nobility. Observant and loyal.

4. **Thomas Whitmore** - Visiting university student, courting Molly. Idealistic, perhaps naive. From a respectable but not wealthy family.

---

## Technical Evaluation

### LLM Options for Character AI

| Option | Cost | Pros | Cons | Recommended For |
|--------|------|------|------|-----------------|
| **Ollama (Local)** | Free | Fully offline, private, no API costs | Requires decent hardware (8GB+ RAM), slower | Development, offline play |
| **OpenAI GPT-3.5** | ~$0.002/1K tokens | Fast, reliable, good quality | Requires API key, ongoing costs | Production with budget |
| **OpenAI GPT-4** | ~$0.03/1K tokens | Excellent quality, nuanced | More expensive | Premium experience |
| **Anthropic Claude** | ~$0.008/1K tokens | Strong reasoning, safe | Requires API key | Production |
| **Google Gemini** | Free tier available | Good quality, free option | Rate limits on free tier | Budget production |
| **Hugging Face (Local)** | Free | Open source, customizable | Complex setup, resource heavy | Advanced customization |
| **Groq** | Free tier | Very fast inference | Limited models, rate limits | Fast prototyping |

**Recommendation for Prototype**:
- **Primary**: Ollama with Llama 2/Mistral for local development (free)
- **Secondary**: OpenAI GPT-3.5-turbo for cloud deployment (low cost)
- **Fallback**: Groq free tier for testing

### Python Game/UI Libraries

| Library | Type | Pros | Cons | Best For |
|---------|------|------|------|----------|
| **Textual** | Terminal UI | Modern, rich, keyboard nav | Terminal only | Quick prototype |
| **Rich** | Terminal UI | Beautiful text, easy | Limited interactivity | Simple display |
| **Pygame** | 2D Graphics | Mature, lots of resources | More complex setup | Full game |
| **Arcade** | 2D Graphics | Modern, easier than Pygame | Less resources | Clean 2D games |
| **Pyglet** | 2D/3D | OpenGL, multimedia | Steeper learning curve | Advanced graphics |
| **Tkinter** | Desktop GUI | Built-in, cross-platform | Dated appearance | Simple desktop |
| **PyQt/PySide** | Desktop GUI | Professional, powerful | Complex, licensing | Desktop apps |
| **Streamlit** | Web UI | Fastest to prototype | Limited interactivity | Web demo |
| **Gradio** | Web UI | Great for ML demos | Limited customization | ML showcases |

**Recommendation for Prototype**:
- **Phase 1**: Rich/Textual for terminal prototype (fastest)
- **Phase 2**: Pygame for graphical version (better experience)
- **Alternative**: Streamlit for web-accessible demo

### Text-to-Speech Options (Optional Voice Output)

| Library | Cost | Quality | Offline | Notes |
|---------|------|---------|---------|-------|
| **pyttsx3** | Free | Basic | Yes | System voices, easy setup |
| **gTTS** | Free | Good | No | Google TTS, requires internet |
| **Coqui TTS** | Free | Excellent | Yes | Neural TTS, resource intensive |
| **ElevenLabs** | Freemium | Premium | No | Best quality, limited free |
| **Bark** | Free | Very Good | Yes | Open source, slow |

**Recommendation**: pyttsx3 for prototype (works offline), Coqui TTS for enhanced version

---

## Architecture

```
game/
├── README.md           # This file
├── requirements.txt    # Dependencies
├── config.py          # Configuration settings
├── main.py            # Entry point
├── characters.py      # Character definitions & personalities
├── llm_interface.py   # LLM provider abstraction
├── game_engine.py     # Core game logic
├── ui_terminal.py     # Terminal-based interface (Rich/Textual)
├── ui_pygame.py       # Pygame graphical interface
└── assets/
    └── background.txt  # ASCII art background (for terminal)
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# For local LLM (optional):
# Install Ollama: https://ollama.ai
# ollama pull mistral
```

## Running the Prototype

### Terminal Version (Default)
```bash
python main.py
```

### With Local LLM (Ollama)
```bash
# First start Ollama with a model
ollama serve
ollama run mistral

# Then run the game
python main.py --llm ollama
```

### With OpenAI
```bash
export OPENAI_API_KEY="your-key-here"
python main.py --llm openai
```

### Pygame Graphical Version
```bash
python main.py --ui pygame
```

## Configuration

Edit `config.py` to customize:
- LLM provider and model
- Character personalities
- Game duration settings
- UI preferences

## Game Flow

1. **Introduction**: Scene is set, victim is revealed
2. **Investigation**: Player asks questions to each suspect
3. **Revelation**: Clues are gathered through responses
4. **Accusation**: Player makes their accusation
5. **Resolution**: True culprit and motive revealed

## Prototype Limitations

- Basic graphics (ASCII/simple sprites)
- Limited conversation memory (last few exchanges)
- No save/load functionality
- Single mystery scenario
- ~5 minute playtime

## Future Enhancements

- [ ] Multiple mystery scenarios
- [ ] Persistent conversation memory
- [ ] Voice synthesis for characters
- [ ] Improved graphics and animations
- [ ] Evidence system and clue tracking
- [ ] Save/load game state
- [ ] Web-based multiplayer version

## License

MIT License - Free to use and modify
