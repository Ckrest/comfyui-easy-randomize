"""
ComfyUI Easy Randomize - Random selection with freeze/lock capability

Workflow: Randomize -> Preview -> Freeze what you like -> Iterate

Nodes:
- ItemPool: Store a pool of items
- RandomSelector: Pick random items from pool
- SmartSelector: Combined pool + selector with freeze
- FreezableInput: Single freezable string input
- FreezableStringCombiner: Combine multiple freezable inputs
- StringJoiner: Join strings with separator
- TemplateFiller: Fill template slots
- SelectionRecorder: Record selections as JSON
- SaveImageWithSelections: Save with selection metadata
- PreviewImageWithText: Preview image with text display
"""

from .random_system import (
    ItemPool,
    RandomSelector,
    SmartSelector,
    FreezableInput,
    FreezableStringCombiner,
    StringJoiner,
    TemplateFiller,
    SelectionRecorder,
    SaveImageWithSelections,
    PreviewImageWithText,
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
)

# WEB_DIRECTORY makes the 'js' folder available to ComfyUI frontend
# Required for FreezableInput widget updates
WEB_DIRECTORY = "js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
