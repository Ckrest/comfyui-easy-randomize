# Notes - ComfyUI Easy Randomize

Brief context for agents working with this package.

## Build / Run

**Installation:**
```bash
# Clone to ComfyUI custom_nodes directory
cd ComfyUI/custom_nodes
git clone https://github.com/Ckrest/comfyui-easy-randomize.git
systemctl --user restart comfyui  # or restart ComfyUI manually
```

**Development:**
- Python changes require ComfyUI restart
- JS changes require browser refresh

## Path Dependencies

| Path | Purpose |
|------|---------|
| `random_system.py` | Random selection nodes |
| `js/FreezableInput.js` | Freeze/lock UI controls |

## Key Features

- Random selection from newline-separated lists
- Freeze button to lock current selection
- Visual indication of frozen state
- Seeds for reproducibility

## Documentation

- `QUICK_START.md` - Quick setup guide
- `RANDOM_SYSTEM_GUIDE.md` - Detailed usage guide
