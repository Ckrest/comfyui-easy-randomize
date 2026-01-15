# Quick Start Guide - Random Selection System

## 5-Minute Setup

### 1. Basic Random Selection

**What you need**: 2 nodes
- ItemPool: Define your items
- RandomSelector: Pick random item(s)

**Setup**:
```
[ItemPool]
└─► pool ─► [RandomSelector] ─► selected_string ─► [Your Prompt Node]
```

**Try it**:
1. Add ItemPool node
2. In items field, type:
   ```
   red shirt
   blue pants
   yellow shoes
   ```
3. Add RandomSelector, connect pool → pool
4. Set count=1, seed=0
5. Run → see random selection!

---

### 2. Freeze to Lock Selection

**After first run**:
1. See what RandomSelector picked (check node output or add SelectionRecorder)
2. Like it? Check the **frozen** checkbox ☑
3. Run again → same selection!
4. Want different? Uncheck frozen ☐, change seed

**This is the killer feature**: Lock what you like, change what you don't.

---

### 3. Combine Multiple Pools

**What you need**: 3+ nodes
- Multiple ItemPools (clothing, backgrounds, lighting)
- RandomSelector for each pool
- StringJoiner to combine results

**Setup**:
```
[Pool: Clothing] → [Random] ─┐
[Pool: Background] → [Random] ─┼─► [StringJoiner] ─► final prompt
[Pool: Lighting] → [Random] ─┘
```

**Freeze selectively**:
- Clothing frozen=☑ → keeps "red dress"
- Background frozen=☐ → tries different backgrounds
- Lighting frozen=☐ → tries different lighting

---

### 4. See What Was Selected

**What you need**: SelectionRecorder

**Setup**:
```
[Random 1] ─► record ─┐
[Random 2] ─► record ─┼─► [SelectionRecorder]
[Random 3] ─► record ─┘
```

**Shows you**:
```
=== Selection Summary ===

1. RandomSelector - clothing 🎲
   Selected: red dress

2. RandomSelector - background 🔒 FROZEN
   Selected: forest

3. RandomSelector - lighting 🎲
   Selected: dramatic
```

Now you know exactly what's in each generation!

---

### 5. Save with Metadata

**What you need**: Replace SaveImage with SaveImageWithSelections

**Setup**:
```
[Image] ─┐
         ├─► [SaveImageWithSelections]
[SelectionRecorder] ─► combined_json ─┘
```

**Result**: Selection data embedded in PNG file forever!

---

## Common Patterns

### Pattern 1: Generate → Review → Freeze → Refine

1. Run with all frozen=☐
2. Review generated images
3. Identify which elements you like
4. Check frozen=☑ on those selectors
5. Re-run with variations on unfrozen parts

### Pattern 2: Template-Based Prompts

```
[Pool: Adj] → [Random] ─┐
[Pool: Char] → [Random] ─┼─► [TemplateFiller]
[Pool: Action] → [Random] ─┤   template: "{slot_1} {slot_2} is {slot_3}"
[Pool: Location] → [Random] ─┘
```

### Pattern 3: Seed Coordination

**Same seed** (items correlate):
```
[Pool A] → [Random seed=42] → "red"
[Pool B] → [Random seed=42] → "roses"
Result: Coordinated colors/themes
```

**Different seeds** (independent):
```
[Pool A] → [Random seed=42] → "red"
[Pool B] → [Random seed=99] → "ocean"
Result: Random combinations
```

---

## Troubleshooting Checklist

- [ ] Pool has items? (not all commented with #)
- [ ] Pool connected to selector?
- [ ] Frozen state as intended? (☑ = locked, ☐ = random)
- [ ] Seed changing if you want new selections?
- [ ] SelectionRecorder connected to see what's selected?

---

## Next Steps

1. **Read full guide**: RANDOM_SYSTEM_GUIDE.md
2. **Experiment with freezing**: This is the most powerful feature
3. **Save with metadata**: Use SaveImageWithSelections to never lose track
4. **Build templates**: TemplateFiller for structured prompts

---

## Quick Reference Card

| Node | Purpose | Key Input |
|------|---------|-----------|
| ItemPool | Store items | items (multiline) |
| RandomSelector | Pick random | count, seed, **frozen** |
| SequentialSelector | Pick by index | index, **frozen** |
| StringJoiner | Combine strings | separator |
| TemplateFiller | Fill template | template + slots |
| SelectionRecorder | Display selections | records 1-10 |
| SaveImageWithSelections | Save with metadata | selection_json |

**Remember**: The frozen checkbox is your best friend!
