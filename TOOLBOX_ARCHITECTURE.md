# Toolbox Architecture

## Overview
Replaced ChromaDB-based memory system with simpler toolbox-based learning:
- **No semantic embeddings** - LLM sees all learned blocks directly
- **No ChromaDB dependency** - Just JSON files
- **User-approved designs become reusable building blocks**

## Structure

```
toolbox/
├── primitives.json          # Hard-coded basic components (never modified)
├── learned_composites.json  # User-approved designs (grows over time)
└── (managed by toolbox_loader.py)
```

## How It Works

### 1. Primitives (Fixed)
- All basic optical components with descriptions
- Organized by category (light sources, beam splitting, detection, etc.)
- Used by LLM when designing new experiments
- Located in `toolbox/primitives.json`

### 2. Learned Composites (Dynamic)
- User-approved experimental designs
- Stored when user clicks "✅ Approve & Store"
- Each composite includes:
  - Full component list
  - Beam paths
  - Physics explanation
  - Simulation results
  - User query and timestamp
- Located in `toolbox/learned_composites.json`

### 3. Design Flow

**Without learned composites:**
```
User query → LLM sees primitives → Designs from scratch → Simulation → Approval
```

**With learned composites:**
```
User query → LLM sees primitives + learned composites
          → Can reuse/adapt past designs → Simulation → Approval → Add to composites
```

## API

### Loading Toolbox
```python
from toolbox_loader import get_toolbox

toolbox = get_toolbox()
composites = toolbox.list_all_composites()
print(f"Toolbox has {len(composites)} learned blocks")
```

### Adding Learned Composite (Auto-called on approval)
```python
toolbox.add_learned_composite(
    composite_id="hom_interferometer_20251120",
    name="Hong-Ou-Mandel Interferometer",
    description="Measures two-photon quantum interference",
    components=[...],  # Full component list
    beam_path=[...],
    physics_explanation="...",
    typical_use="Verifying photon indistinguishability",
    full_design={...}  # Complete design dict
)
```

### Getting Toolbox Info for LLM
```python
# Get formatted text for LLM prompts
primitives_text = toolbox.get_primitives_for_llm()
composites_text = toolbox.get_composites_for_llm()
full_toolbox = toolbox.get_full_toolbox_for_llm()
```

## Benefits Over ChromaDB

✅ **Simpler** - Just JSON files, no database
✅ **Transparent** - Can view/edit learned_composites.json directly  
✅ **Faster** - No embedding computation
✅ **Scalable** - LLM context handles 100+ composites easily
✅ **Portable** - Share toolbox by copying JSON files
✅ **Debuggable** - Clear what LLM sees, no hidden similarity scores

## Migration Notes

- Old memory in `memory_backup_old/` (63MB)
- 26 previous experiments not migrated (can be manually added if needed)
- New system starts fresh, learns from new approvals
- No functionality lost - system still learns, just simpler mechanism

## Future Enhancements

- Export/import toolbox between users
- Composite categorization (HOM, Bell states, etc.)
- Composite editing interface
- Usage statistics (which composites used most often)
