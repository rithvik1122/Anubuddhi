# Aṇubuddhi (अणुबुद्धि) - AI-Powered Quantum Experiment Designer

**Atomic Intelligence for Quantum Optics Experiment Design**

An LLM-based agentic AI system that learns from experience to design quantum optics experiments automatically.

## 🚀 Quick Start

```bash
./launch.sh
```

Or manually:
```bash
conda run -n agentic-quantum streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## ✨ Key Features

### 🧠 Memory System - AI That Learns!
- **Episodic Memory**: Stores every experiment design with full context
- **Procedural Memory**: Auto-extracts building blocks (Bell state prep, HOM interferometer, etc.)
- **Semantic Search**: Retrieves relevant past work for new designs
- **Prompt Augmentation**: LLM gets enhanced prompts with your past experience

### ⚗️ Intelligent Design Process
- **Web-Enhanced**: Searches for relevant experimental data online
- **Self-Correcting**: Validates and refines designs automatically (up to 3 cycles)
- **Building Block Reuse**: Composes complex experiments from learned patterns
- **No Timeouts**: Complex designs get the time they need (2-3 minutes)

### 📊 Rich User Interface
- **5 Tabs**: Component justifications, overview, beam paths, raw data, memory & learn
- **System Status Sidebar**: Shows API and memory status
- **Progress Indicators**: Clear feedback on what's happening
- **Error Messages**: Helpful guidance when things go wrong

## 📁 Important Files

### Launch Scripts
- `./launch.sh` - Interactive setup and launch (RECOMMENDED)
- `./run_app.sh` - Quick launch without checks
- `app.py` - Main Streamlit application

### Testing
- `test_api_credits.py` - Check OpenRouter API status
- Quick test: `python test_api_credits.py`

### Documentation
- `MEMORY_FIX_SUMMARY.md` - How memory system was fixed
- `UI_IMPROVEMENTS.md` - Progress indicator improvements
- `NO_TIMEOUT_DESIGN.md` - Why we removed timeouts
- `MEMORY_IMPLEMENTATION_GUIDE.md` - Memory architecture details

### Configuration
- `.env` - API keys (OPENAI_API_KEY for OpenRouter)
- `./memory/` - ChromaDB storage (created on first run)

## 🎯 How to Use

### 1. Launch the App
```bash
./launch.sh
```

### 2. Check System Status (Sidebar)
- ✅ API Key: Configured
- ✅ Memory: Active (after first design)

### 3. Design Your First Experiment
Enter a query like:
```
Design a Bell state generator with maximum entanglement
```

**What happens:**
- 🔍 Analyzes requirements (5s)
- 🌐 Searches web for context (10s)
- ⚗️ Designs experiment (30-90s)
- ✅ Validates physics (5s)
- 🎨 Renders diagram (5s)
- 💾 Stores in memory automatically

**Watch the terminal** for detailed progress:
```
🤖 Starting design for: design a Bell state generator
🧠 Searching memory for relevant experience...
📚 Current knowledge: 0 experiments, 0 building blocks

======================================================================
🔄 Refinement Cycle 1/3
======================================================================
🤖 Generating initial design...
✅ LLM responded with 2847 characters
✅ Parsed design with 8 components
🔍 Validating design...
✅ Design validated successfully!
🎉 Final design ready after 1 cycle(s)

✅ Design stored as exp_20251018_143052
📚 Total knowledge: 1 experiments, 3 building blocks
⏱️  Design took 45.3 seconds
```

### 4. Check Memory Tab
Click "💬 Memory & Learn" to see:
- Statistics (1 experiment stored, N building blocks)
- Experience level
- Browsable building blocks
- Search past experiments

### 5. Design Something Related
Enter:
```
Design quantum teleportation
```

**Now the magic happens:**
```
🧠 Searching memory for relevant experience...
📚 Found 1 similar past experiments
🔧 Found 3 relevant building blocks
   • Bell state preparation (PBS + HWP + SPDC)
   • Beam splitter interference
   • Coincidence detection
```

The LLM now receives:
- Your previous Bell state design
- Extracted building blocks with full component details
- Instructions to reuse rather than start from scratch

**Result:** Faster, more consistent, better designs! 🎉

## ⏱️ Expected Timing

| Design Type | Time | Why |
|------------|------|-----|
| Simple (Bell state) | 30-60s | Single pattern, quick validation |
| Medium (HOM) | 45-90s | Multiple components, one refinement cycle |
| Complex (Teleportation) | 90-180s | Many components, 2-3 refinement cycles |
| Very Complex (>15 components) | 2-4 min | Extensive validation, multiple cycles |

**Don't worry if it takes time!** Complex designs need it. Watch the terminal for progress.

## 🔧 Troubleshooting

### App Gets Stuck at "Designing experiment"
**Check terminal output:**
- If you see refinement cycles → It's working! Just wait
- If no output for 5+ minutes → Problem

**Solutions:**
1. Test API: `python test_api_credits.py`
2. Check credits: https://openrouter.ai/credits
3. Check OpenRouter status: https://status.openrouter.ai/

### "Insufficient credits" Error
```bash
# Add credits at OpenRouter
https://openrouter.ai/credits

# Then restart app
./launch.sh
```

### "Memory system not initialized"
This is normal **before your first design**. Once you generate a design, memory will show as active.

### Embedding Model Download Slow
```bash
# Pre-download (79MB, one-time):
conda run -n agentic-quantum python -c "
from chromadb.utils import embedding_functions
ef = embedding_functions.DefaultEmbeddingFunction()
"
```

### Wrong Conda Environment
Always launch with:
```bash
./launch.sh
# OR
conda run -n agentic-quantum streamlit run app.py
```

**NOT:**
```bash
streamlit run app.py  # ❌ Wrong! Uses base environment
```

## 📚 Memory System Details

### What Gets Stored
- Complete experiment design (title, description, components, beam paths)
- User query and timestamp
- Component justifications
- Physics explanations
- Automatically extracted building blocks

### Building Block Patterns Detected
1. **Bell State Preparation**: PBS + HWP + SPDC source
2. **HOM Interferometer**: Beam splitter + 2 detectors
3. **Beam Expansion**: 2+ lenses in sequence
4. **Double-Slit**: Double slit + detection screen

### How Memory Enhances Designs
When you ask for a new design, the system:
1. Searches past experiments (semantic similarity)
2. Retrieves relevant building blocks (pattern matching)
3. Augments LLM prompt with:
   - Top 2 similar experiments
   - Top 3 relevant building blocks
   - Full component details (type, parameters, position)
   - Instruction to reuse and adapt

### Result
- **Consistency**: Reuses proven designs
- **Speed**: Less exploration, more refinement
- **Quality**: Builds on what works
- **Complexity**: Composes simple patterns into complex experiments

## 🎓 Example Workflow

### Day 1: Learn Basics
```
1. Design a Bell state generator
   → Stores Bell state pattern
2. Design a HOM interferometer
   → Stores HOM pattern
3. Design beam expansion telescope
   → Stores beam expansion pattern
```

**Memory now has 3 experiments, ~9 building blocks**

### Day 2: Build Complex Systems
```
4. Design quantum teleportation
   → Retrieves Bell state + HOM patterns
   → Combines them intelligently
   → Adds classical channels
   → Result: Complete teleportation setup in 90s

5. Design quantum key distribution (BB84)
   → Retrieves Bell state + beam expansion
   → Adds polarization analysis
   → Result: Secure QKD system
```

**Memory grows with each design, AI gets smarter!**

## 🌟 Tips for Best Results

1. **Be Specific**: "Design a Bell state generator with SPDC and PBS"
2. **Watch Terminal**: Detailed progress logs
3. **Don't Refresh**: Lose design in progress
4. **Build Progressively**: Simple → Complex
5. **Check Memory Tab**: See what AI has learned
6. **Reuse Patterns**: "Design X using Y pattern from memory"

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  Streamlit UI (app.py)                          │
│  • 5-tab interface                              │
│  • System status sidebar                        │
│  • Progress indicators                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  LLM Designer (llm_designer.py)                 │
│  • Self-correction loop (max 3 cycles)          │
│  • Web search integration                       │
│  • Memory-augmented prompts                     │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼────────────────────────┐
│  SimpleLLM   │  │  ExperimentMemory             │
│  OpenRouter  │  │  (memory_system.py)           │
│  Claude 3.5  │  │  • ChromaDB storage           │
└──────────────┘  │  • Pattern detection          │
                  │  • Semantic search            │
                  │  • Prompt augmentation        │
                  └───────────────────────────────┘
```

## 📞 Support

**Check these first:**
1. Terminal output (most informative!)
2. Sidebar status (API, Memory)
3. `test_api_credits.py` output
4. Documentation in `*.md` files

**Common issues covered in:**
- `MEMORY_FIX_SUMMARY.md` - Memory not working
- `UI_IMPROVEMENTS.md` - UI getting stuck
- `NO_TIMEOUT_DESIGN.md` - Understanding timing

## 🎉 You're Ready!

```bash
./launch.sh
```

Design your first quantum experiment and watch the AI learn! 🚀✨

---

**Made with ❤️ for Quantum Physicists by AI Researchers**
