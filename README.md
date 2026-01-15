# ComfyUI Easy Randomize

![AI-Assisted](https://img.shields.io/badge/AI-Assisted-blue)

Random selection nodes with freeze/lock capability for iterative prompt building.

**Workflow:** Randomize → Preview → Freeze what you like → Iterate on the rest

## Features

- **Item Pools** - Define lists of items (styles, characters, settings, etc.)
- **Random Selection** - Pick random items from pools
- **Freeze/Lock** - Lock selections you like, keep randomizing the rest
- **Sequential Mode** - Step through items in order
- **Save with Metadata** - Embed selection data in saved images

## Nodes

| Node | Purpose |
|------|---------|
| **Item Pool** | Store a pool of items (one per line) |
| **Random Selector** | Pick random items from a pool |
| **Smart Selector** | Combined pool + selector with freeze, supports file loading |
| **Freezable Input** | Single string input that can be frozen |
| **Freezable String Combiner** | Combine up to 10 freezable inputs |
| **String Joiner** | Join multiple strings with separator |
| **Template Filler** | Fill template slots with values |
| **Selection Recorder** | Record selections as JSON |
| **Save Image (with Selections)** | Save image with selection metadata |
| **Preview Image + Text** | Preview image with synced text display |

## Installation

1. Clone or download to `ComfyUI/custom_nodes/`:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/Ckrest/comfyui-easy-randomize.git
   ```

2. Restart ComfyUI

3. Nodes appear under **Easy Randomize** category

## Quick Start

See [QUICK_START.md](QUICK_START.md) for a 5-minute tutorial.

## The Freeze Workflow

1. **Set up pools** - Create Item Pool nodes with your options
2. **Connect to selectors** - Use Random Selector or Smart Selector
3. **Run the workflow** - See what gets selected
4. **Freeze what you like** - Check the `frozen` checkbox on good selections
5. **Run again** - Frozen values stay, others get new random picks
6. **Iterate** - Keep freezing until you have the perfect combination

## License

MIT License - See [LICENSE](LICENSE)
