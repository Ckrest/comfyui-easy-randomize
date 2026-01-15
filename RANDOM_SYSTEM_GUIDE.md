# Random Selection System - User Guide

## Overview

The Random Selection System provides powerful, reproducible randomness control for ComfyUI workflows. It solves two key problems:

1. **Selection Tracking**: Always know what random items were used in each generated image
2. **Reproducibility**: Freeze selections to re-run with same elements but different generation seeds

## Core Concepts

### The Freeze Toggle 🔒

Every selector has a **frozen** checkbox:
- **Unchecked (🎲)**: Generates new random selection each run
- **Checked (🔒)**: Keeps the current selection, doesn't re-roll

This lets you:
- Generate multiple variations with different random elements
- Lock in what you like and only change specific parts
- Re-run with same prompt elements but different image seeds

### Selection Records 📋

All selectors output selection records that track:
- What items were available in the pool
- What items were actually selected
- The seed used
- Whether it was frozen
- Timestamp

These records are:
- Displayed in the UI via SelectionRecorder
- Embedded in saved images via SaveImageWithSelections
- Stored with the workflow for full reproducibility

## Node Reference

### 1. Item Pool

**Purpose**: Define a pool of items to select from

**Inputs**:
- `items` (multiline text): One item per line
- `pool_name`: Name for this pool (appears in records)

**Features**:
- Comment out items with `#` prefix
- Reorder items by moving lines
- Empty lines are ignored

**Example**:
```
red shirt
blue pants
#green hat
yellow shoes
```

**Outputs**:
- `pool`: Pool data structure (connect to selectors)
- `items_list`: String list of active items (for display/debug)

---

### 2. Random Selector 🎲

**Purpose**: Randomly select N items from a pool

**Inputs**:
- `pool` (optional): Pool from ItemPool node
- `items_text` (optional): Or paste items directly, one per line
- `count`: How many items to select
- `seed`: Random seed (change for different selections)
- `frozen` 🔒: Lock current selection
- `allow_duplicates`: Allow same item multiple times

**Outputs**:
- `selected_items`: Selected items as string
- `selected_string`: Same (for convenience)
- `selection_record`: Metadata for tracking

**Workflow**:
1. First run: Unchecked frozen → selects random items
2. See what was selected in SelectionRecorder
3. Like the result? Check frozen 🔒
4. Next runs: Same items selected, can tweak other parts

---

### 3. Sequential Selector 🔢

**Purpose**: Select items by index/position (not random)

**Use Cases**:
- Cycle through items in order for animation
- Batch processing: frame 0 → item 0, frame 1 → item 1
- Controlled iteration

**Inputs**:
- `pool` or `items_text`: Source items
- `index`: Which item to start at (0-based)
- `count`: How many sequential items
- `wrap`: Loop back to start if index exceeds pool size
- `frozen` 🔒: Lock current selection

**Example**:
Pool: `["A", "B", "C", "D"]`
- index=0, count=1 → "A"
- index=2, count=2 → "C, D"
- index=3, count=2, wrap=true → "D, A"

---

### 4. String Joiner ➕

**Purpose**: Combine multiple strings with a separator

**Inputs**:
- `separator`: String between items (default: ", ")
- `string_1` through `string_10`: Up to 10 strings to join

**Features**:
- Automatically filters empty strings
- Trims whitespace

**Example**:
```
string_1: "red shirt"
string_2: "forest background"
string_3: ""
separator: ", "

Result: "red shirt, forest background"
```

---

### 5. Template Filler 📝

**Purpose**: Fill a template with values from different sources

**Inputs**:
- `template`: String with `{slot_1}` placeholders
- `slot_1` through `slot_10`: Values to fill in

**Example**:
```
template: "A {slot_1} {slot_2} wearing {slot_3}, {slot_4} lighting"
slot_1: "tall"
slot_2: "woman"
slot_3: "red dress"
slot_4: "dramatic"

Result: "A tall woman wearing red dress, dramatic lighting"
```

**Advanced**: Use descriptive names in your workflow by connecting outputs to specific slots

---

### 6. Selection Recorder 📋

**Purpose**: Display all current selections in readable format

**Inputs**:
- `record_1` through `record_10`: Selection records from selectors

**Outputs**:
- `combined_json`: All records as JSON
- `display_text`: Human-readable summary (shown in UI)

**Display Format**:
```
=== Selection Summary ===

1. RandomSelector - clothing_pool 🎲 Random
   Selected: blue pants

2. RandomSelector - background_pool 🔒 FROZEN
   Selected: forest

Total: 2 selections, 1 frozen
```

---

### 7. Save Image (with Selections) 💾

**Purpose**: Save images with selection metadata embedded

**Inputs**:
- `images`: Images to save
- `filename_prefix`: Filename prefix
- `selection_json`: JSON from SelectionRecorder (optional)

**Features**:
- Drop-in replacement for standard SaveImage node
- Embeds selection data in PNG metadata
- Selection records are saved with the image forever
- Can extract metadata later to reproduce exact prompt

**Metadata Location**:
- Embedded in PNG file (standard ComfyUI format)
- Visible in PNG metadata readers
- Preserved when sharing files

---

## Example Workflows

### Basic Random Composition

```
[Item Pool: Clothing]
  items: "red shirt\nblue pants\nyellow shoes"
  ↓
[Random Selector]
  count: 1
  seed: 42
  frozen: ☐
  ↓
  selected_string: "blue pants"

[Item Pool: Backgrounds]
  items: "forest\ncity\nbeach"
  ↓
[Random Selector]
  count: 1
  seed: 42
  frozen: ☐
  ↓
  selected_string: "forest"

↓ ↓
[String Joiner]
  separator: ", "
  ↓
  "blue pants, forest"
  ↓
[Text to CLIP]
```

### Freeze Workflow (Re-run with locked elements)

**First Run**:
1. Generate image with frozen=☐ on all selectors
2. See results: "blue pants, forest, dramatic lighting"
3. Like clothing and background, want different lighting

**Second Run**:
1. Check frozen=☑ on clothing and background selectors
2. Leave frozen=☐ on lighting selector
3. Change lighting selector's seed
4. Generate → "blue pants, forest, soft lighting"

Only the lighting changed!

### Template-Based Generation

```
[Item Pool: Adjectives] → [Random] → "tall"
[Item Pool: Characters] → [Random] → "warrior"
[Item Pool: Actions] → [Random] → "running"
[Item Pool: Locations] → [Random] → "mountain path"
                            ↓ ↓ ↓ ↓
                    [Template Filler]
  template: "A {slot_1} {slot_2} {slot_3} through a {slot_4}"
                            ↓
  Result: "A tall warrior running through a mountain path"
```

### Batch Animation (Sequential Selection)

```
[Item Pool: Frames]
  items: "frame_a\nframe_b\nframe_c\nframe_d"
  ↓
[Sequential Selector]
  index: 0  ← increment this for each frame
  count: 1
  wrap: true
  ↓
Frame 0: "frame_a"
Frame 1: "frame_b"
Frame 2: "frame_c"
Frame 3: "frame_d"
Frame 4: "frame_a" (wrapped)
```

---

## Tips & Best Practices

### Organization
- **Name your pools descriptively**: "character_clothing", "scene_backgrounds", "lighting_styles"
- **Group related items**: Keep similar items in same pool
- **Comment liberally**: Use `#` to temporarily disable items without deleting them

### Seed Management
- **Same seed across selectors**: For correlated randomness (clothing + matching accessories)
- **Different seeds**: For independent randomness (character + unrelated background)
- **Seed + batch number**: For variations in batch processing

### Freezing Strategy
- **Start unfrozen**: Generate a few times to see options
- **Freeze what works**: Lock good elements progressively
- **Unfreeze to experiment**: Try alternatives for specific parts

### Reproducibility
1. Use SelectionRecorder on all your selectors
2. Connect to SaveImageWithSelections
3. Selection data is embedded in PNG
4. Can always see what elements created each image

### Avoiding Confusion
- **One selector per pool type**: Don't have 3 random clothing selectors with different seeds
- **Use descriptive outputs**: Connect records to recorder so you can see what's happening
- **Check frozen state**: Easy to forget a frozen selector and wonder why it's not changing

---

## Troubleshooting

**Problem**: Selector always outputs the same thing
- **Solution**: Check if frozen=☑, uncheck to allow new selections

**Problem**: Can't see what was selected
- **Solution**: Connect selection_record outputs to SelectionRecorder node

**Problem**: Selection changes when I don't want it to
- **Solution**: Check frozen=☑ on that selector

**Problem**: Pool has no items
- **Solution**: Check for `#` comments, empty lines, or verify pool is connected

**Problem**: Template has missing values
- **Solution**: Ensure all referenced slots have inputs connected

---

## Node Compatibility

### Works With:
- Any STRING input (CLIP Text Encode, Display Text, etc.)
- Standard SaveImage (use SaveImageWithSelections instead for metadata)
- Batch processing (use Sequential Selector with frame index)
- Wildcard systems (pool items can contain wildcards if your workflow supports them)

### Output Types:
- `STRING`: Standard ComfyUI string, works everywhere
- `POOL`: Custom type, only connects to selector nodes
- `SELECTION_RECORD`: Custom type, connects to SelectionRecorder

---

## Advanced: Understanding State Persistence

**How Freezing Works**:
- Each selector stores its last selection in a global dictionary
- Key is the node's unique_id (persists during ComfyUI session)
- When frozen=☑, uses stored selection instead of re-rolling
- State is lost when ComfyUI restarts (intentional, clean slate)

**When State is Updated**:
- Every time frozen=☐ and node executes
- NOT updated when frozen=☑ (that's the point!)

**Implications**:
- Freeze state is workflow-specific (different workflows = different state)
- Copying a node creates new state (new unique_id)
- Restarting ComfyUI clears all frozen selections (re-run to populate)

---

## Future Enhancements (Not Yet Implemented)

Potential additions based on user feedback:

- **Weighted Selection**: Items with weights (requires extending pool format)
- **Conditional Selection**: Rules like "if X then Y"
- **Selection History**: "Don't repeat last 5 selections"
- **Pool Merger**: Combine multiple pools into one
- **Batch Variation Generator**: Generate N variations in one run
- **Load Selection from File**: Paste saved JSON to reproduce exact setup

Let me know what features you'd find most useful!

---

## Questions?

This system is designed to be simple but powerful. If you have questions or find edge cases, please let me know!
