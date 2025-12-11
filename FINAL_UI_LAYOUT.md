# Always-On Two-Pane Layout - Final UI Structure

## Overview
The UI now features a permanent two-column layout with the Aṇubuddhi header always visible at the top. The chat input is fixed at the bottom of the left pane (ChatGPT-style), and there's no transition or welcome screen—users are immediately ready to start chatting.

## Final Structure

```
┌───────────────────────────────────────────────────────────────┐
│              Aṇubuddhi (अणुबुद्धि)                            │
│       Atomic Intelligence for Quantum Experiment Design       │
├──────────────────────┬────────────────────────────────────────┤
│ 💬 Conversation      │  ⚛️  Your Design Will Appear Here     │
│                      │                                        │
│   [Welcome message]  │  (Or optical table + design details)  │
│   ✨                 │                                        │
│   I can help you:    │                                        │
│   • Design experiments│                                       │
│   • Answer questions │                                        │
│   • Refine setups    │                                        │
│   • Learn & improve  │                                        │
│                      │                                        │
│ ────────────────────│                                        │
│ [Chat messages]      │                                        │
│                      │                                        │
│ ────────────────────│                                        │
│ [Message input]      │                                        │
│ [💬 Send] [🆕 New]   │                                        │
└──────────────────────┴────────────────────────────────────────┘
```

## Key Changes

### 1. **Header Always Visible**
- Title and subtitle now appear at the very top of the page
- Always present regardless of whether a design exists
- Clean separator line below header

### 2. **Two-Column Layout Always Present**
- No transition animation needed
- Left: Chat pane (50% width)
- Right: Design pane (50% width)
- `gap="large"` for proper spacing

### 3. **Left Pane: Chat Interface**

#### When No Conversation
```html
✨ Welcome to Aṇubuddhi

I'm your quantum optics AI consultant. I can help you:
🔬 Design experiments from scratch
💬 Answer questions about quantum physics
🔧 Refine setups iteratively
📚 Learn from experience and suggest improvements

Type your first message below to get started!
```

#### When Conversation Exists
- Scrollable message area
- User messages: left-aligned, blue gradient
- AI messages: slightly right-offset, golden gradient  
- Chat bubbles with proper styling

#### Chat Input (Always at Bottom)
- Sticky positioning at bottom of left pane
- Placeholder: `"Design a Bell state generator... or ask: 'What is SPDC?'"`
- **Send button**: Primary action
- **New button**: Only appears when a design exists

### 4. **Right Pane: Design Visualization**

#### When No Design
```html
⚛️
Your Design Will Appear Here

Start by typing a message in the chat on the left.
I'll design the experiment and show the optical table here!
```

#### When Design Exists
- **Experience badge**: Shows if memory was used
- **Web search badge**: Shows if online research was used
- **Optical Setup**: Large diagram (12x8 figsize)
- **Design Details Tabs**:
  - ⚙️ Component Selection (justifications)
  - 📋 Overview (title, description, physics)
  - 🌊 Beam Paths (light propagation)
  - 🔧 Raw Data (LLM response, parsed JSON)
  - 💬 Memory & Learn (knowledge stats)

## User Flow

### First-Time Experience
1. **User arrives**: Sees header + two-pane layout immediately
2. **Left pane**: Welcome message explaining capabilities
3. **Right pane**: Placeholder message
4. **User types**: "Design a Bell state generator"
5. **Left pane**: User message appears → AI processing → AI response
6. **Right pane**: Optical table + design details appear
7. **Chat input**: Still at bottom-left, ready for next message

### Conversational Flow
```
User: "Design a Bell state generator"
→ [Design mode] Creates design

[Left: chat shows conversation]
[Right: optical table + tabs]

User: "Why did you use BBO?"
→ [Chat mode] AI explains, no design change

[Left: question + answer appear in chat]
[Right: design unchanged]

User: "Add polarizers"
→ [Design mode] Updates design

[Left: request + confirmation in chat]
[Right: updated optical table]
```

## CSS Classes

### Layout
```css
.main-header          - Title styling
.subtitle             - Subtitle styling  
.chat-messages        - Scrollable chat area (max 70vh)
.chat-input-container - Sticky bottom input area
.user-message         - Left-aligned user bubbles
.ai-message           - Right-offset AI bubbles
```

### Welcome Message Styles
- Centered layout with icons
- Color scheme matches dark warm theme
- Clear hierarchy (icon → title → description)

## Benefits

### User Experience
✅ **No confusion**: Clear, consistent layout from start
✅ **No waiting**: Immediate interaction, no splash screen
✅ **Natural flow**: Chat on left, results on right (like split-screen IDEs)
✅ **ChatGPT familiar**: Input at bottom feels natural
✅ **Always accessible**: Title always visible for branding

### Technical
✅ **Simpler code**: No conditional rendering for transitions
✅ **No animation bugs**: Removed complex CSS transitions
✅ **Faster load**: No need to wait for animation
✅ **Easier maintenance**: Single layout structure

## Removed Features

- ❌ Centered welcome screen
- ❌ Transition animation from welcome → two-column
- ❌ "Design" button in center (replaced with chat-only interface)
- ❌ Separate welcome form (unified chat interface)

## Files Modified

### `app.py`
- Removed welcome screen conditional rendering
- Moved header outside columns (always visible)
- Created persistent two-column structure
- Added welcome messages for both empty panes
- Fixed chat input to bottom of left column
- Added proper right pane content for both states

## Code Structure

```python
# Header (always visible)
st.markdown('Aṇubuddhi title...')
st.markdown('subtitle...')

# Two-column layout (always present)
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("### 💬 Conversation")
    
    # Chat messages (scrollable)
    if conversation_context:
        for msg in conversation_context:
            # Render user/AI messages
    else:
        # Welcome message
    
    # Chat input (sticky bottom)
    with st.form("chat_form"):
        chat_text = st.text_input(...)
        send / new buttons

with right_col:
    if current_design:
        # Show optical table + tabs
    else:
        # Show placeholder message
```

## Testing Checklist

- [x] Header visible on page load
- [x] Two columns present from start
- [x] Welcome message in left pane (no design)
- [x] Placeholder in right pane (no design)
- [x] Chat input at bottom-left
- [x] Send button works for first message
- [x] New button appears after design created
- [x] Design appears in right pane
- [x] Chat messages scroll independently
- [x] Input stays at bottom while scrolling
- [x] Dual-mode routing works (chat vs design)
- [x] No errors in console
- [x] Responsive to window size

## Conclusion

The final UI provides a clean, professional, always-ready interface that matches modern AI chat applications. Users immediately understand how to interact (type in the chat), and the consistent layout eliminates confusion from transitions or changing structures.
