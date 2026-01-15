"""
ComfyUI Easy Randomize - Random selection with freeze/lock capability.

Workflow: Randomize -> Preview -> Freeze what you like -> Iterate on the rest.
"""

import random
import json
import sys
import os
from datetime import datetime

# Import SaveImage from ComfyUI nodes for inheritance
comfy_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if comfy_path not in sys.path:
    sys.path.insert(0, comfy_path)

from nodes import SaveImage
import folder_paths


class ItemPool:
    """Stores a pool of items, one per line."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "items": ("STRING", {"multiline": True, "default": "item1\nitem2\nitem3"}),
                "pool_name": ("STRING", {"default": "my_pool"}),
            }
        }

    RETURN_TYPES = ("POOL", "STRING")
    RETURN_NAMES = ("pool", "items_list")
    FUNCTION = "create_pool"
    CATEGORY = "Easy Randomize"

    def create_pool(self, items, pool_name):
        lines = items.strip().split('\n')
        parsed_items = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        pool_data = {"name": pool_name, "items": parsed_items, "count": len(parsed_items)}
        return (pool_data, "\n".join(parsed_items))


class RandomSelector:
    """Randomly selects N items from a pool.

    When frozen=True: Uses the display widget value (preserves last selection).
    When frozen=False: Generates new random selection each execution.

    The display widget stores the frozen value (persisted in workflow JSON).
    Use frozen=True for reproducibility (locks the current selection).
    """

    @classmethod
    def IS_CHANGED(cls, count, frozen, allow_duplicates, display, pool=None):
        """Force re-execution when not frozen to ensure fresh randomness per queue item."""
        if frozen:
            # Frozen: allow caching (return stable value)
            return display
        # Not frozen: force re-execution by returning NaN (NaN != NaN is always True)
        return float("nan")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "count": ("INT", {"default": 1, "min": 1, "max": 100}),
                "frozen": ("BOOLEAN", {"default": False}),
                "allow_duplicates": ("BOOLEAN", {"default": False}),
                "display": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "pool": ("POOL",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected",)
    FUNCTION = "select"
    OUTPUT_NODE = True
    CATEGORY = "Easy Randomize"

    def select(self, count, frozen, allow_duplicates, display, pool=None):
        if pool is None:
            return {"ui": {"display": [""]}, "result": ("",)}

        source_items = pool["items"]
        if not source_items:
            return {"ui": {"display": [""]}, "result": ("",)}

        if frozen:
            # FROZEN: Use display widget value
            result = display if display else ""
            return {"ui": {}, "result": (result,)}
        else:
            # NOT FROZEN: Generate new random selection (no seed = true randomness)
            if allow_duplicates:
                selected = random.choices(source_items, k=min(count, len(source_items) * 100))
            else:
                selected = random.sample(source_items, k=min(count, len(source_items)))
            result = ", ".join(selected)
            return {"ui": {"display": [result]}, "result": (result,)}


# SequentialSelector removed - functionality merged into SmartSelector


class StringJoiner:
    """Joins multiple strings with a separator."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "separator": ("STRING", {"default": ", "}),
            },
            "optional": {
                "string_1": ("STRING", {"forceInput": True}),
                "string_2": ("STRING", {"forceInput": True}),
                "string_3": ("STRING", {"forceInput": True}),
                "string_4": ("STRING", {"forceInput": True}),
                "string_5": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "join"
    CATEGORY = "Easy Randomize"

    def join(self, separator, **kwargs):
        parts = []
        for i in range(1, 6):
            value = kwargs.get(f"string_{i}", "")
            if value and value.strip():
                parts.append(value.strip())
        return (separator.join(parts),)


class FreezableInput:
    """Single freezable string input.

    When frozen=True: Uses the display widget value (ignores wire even if connected).
    When frozen=False: Uses wire input if connected, otherwise empty (flush behavior).

    The display widget serves dual purpose:
    - Shows the current value being used
    - Stores the frozen value (persisted in workflow JSON)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frozen": ("BOOLEAN", {"default": False}),
                "display": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "text": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "process"
    OUTPUT_NODE = True
    CATEGORY = "Easy Randomize"

    def process(self, frozen, display, text=None):
        if frozen:
            # FROZEN: Widget value wins, even if wire is connected
            result = display
            # Don't update UI - preserve the frozen value in widget
            return {"ui": {}, "result": (result,)}
        else:
            # NOT FROZEN: Wire value or empty (flush behavior)
            result = text if text is not None else ""
            # Update display widget to show current value (clears if no wire)
            return {"ui": {"display": [result]}, "result": (result,)}


class FreezableStringCombiner:
    """Combines up to 10 freezable string inputs.

    Each slot has:
    - text_N: Display widget (stores the value, persisted in workflow JSON)
    - input_N: Optional wire input (forceInput, for connecting other nodes)
    - freeze_N: Toggle to lock the value

    When frozen: Uses text_N widget value, ignores input_N wire
    When not frozen: Uses input_N if connected, otherwise empty (flush behavior)

    The text_N widgets store frozen values (persisted in workflow JSON).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Slot 1
                "text_1": ("STRING", {"default": "", "multiline": True}),
                "freeze_1": ("BOOLEAN", {"default": False}),
                # Slot 2
                "text_2": ("STRING", {"default": "", "multiline": True}),
                "freeze_2": ("BOOLEAN", {"default": False}),
                # Slot 3
                "text_3": ("STRING", {"default": "", "multiline": True}),
                "freeze_3": ("BOOLEAN", {"default": False}),
                # Slot 4
                "text_4": ("STRING", {"default": "", "multiline": True}),
                "freeze_4": ("BOOLEAN", {"default": False}),
                # Slot 5
                "text_5": ("STRING", {"default": "", "multiline": True}),
                "freeze_5": ("BOOLEAN", {"default": False}),
                # Slot 6
                "text_6": ("STRING", {"default": "", "multiline": True}),
                "freeze_6": ("BOOLEAN", {"default": False}),
                # Slot 7
                "text_7": ("STRING", {"default": "", "multiline": True}),
                "freeze_7": ("BOOLEAN", {"default": False}),
                # Slot 8
                "text_8": ("STRING", {"default": "", "multiline": True}),
                "freeze_8": ("BOOLEAN", {"default": False}),
                # Slot 9
                "text_9": ("STRING", {"default": "", "multiline": True}),
                "freeze_9": ("BOOLEAN", {"default": False}),
                # Slot 10
                "text_10": ("STRING", {"default": "", "multiline": True}),
                "freeze_10": ("BOOLEAN", {"default": False}),
                # Bottom controls
                "separator": ("STRING", {"default": ", "}),
                "freeze_all": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                # Wire inputs (forceInput - connection-only, no widget)
                "input_1": ("STRING", {"forceInput": True}),
                "input_2": ("STRING", {"forceInput": True}),
                "input_3": ("STRING", {"forceInput": True}),
                "input_4": ("STRING", {"forceInput": True}),
                "input_5": ("STRING", {"forceInput": True}),
                "input_6": ("STRING", {"forceInput": True}),
                "input_7": ("STRING", {"forceInput": True}),
                "input_8": ("STRING", {"forceInput": True}),
                "input_9": ("STRING", {"forceInput": True}),
                "input_10": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "combine"
    OUTPUT_NODE = True
    CATEGORY = "Easy Randomize"

    def combine(self, separator, freeze_all, **kwargs):
        values = []
        ui_updates = {}

        for i in range(1, 11):
            text_widget = kwargs.get(f"text_{i}", "") or ""
            wire_input = kwargs.get(f"input_{i}")  # None if not connected
            is_frozen = kwargs.get(f"freeze_{i}", False) or freeze_all

            if is_frozen:
                # FROZEN: Widget value wins, ignore wire even if connected
                result = text_widget
                # Don't update UI - preserve the frozen value in widget
            else:
                # NOT FROZEN: Wire value or empty (flush behavior)
                result = wire_input if wire_input is not None else ""
                # Update widget to show current value (clears if no wire)
                ui_updates[f"text_{i}"] = [result]

            if result:
                values.append(result)

        combined = separator.join(values)

        return {"ui": ui_updates, "result": (combined,)}


class TemplateFiller:
    """Fills a template with slot values."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {"multiline": True, "default": "{slot_1} {slot_2}"}),
            },
            "optional": {
                "slot_1": ("STRING", {"forceInput": True}),
                "slot_2": ("STRING", {"forceInput": True}),
                "slot_3": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "fill"
    CATEGORY = "Easy Randomize"

    def fill(self, template, **kwargs):
        replacements = {f"slot_{i}": kwargs.get(f"slot_{i}", "") or "" for i in range(1, 4)}
        try:
            result = template.format(**replacements)
        except KeyError as e:
            result = f"[Template Error: Missing {e}]"
        return (result,)


class SelectionRecorder:
    """Records selections as JSON."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "text_1": ("STRING", {"forceInput": True}),
                "text_2": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json_output",)
    FUNCTION = "record"
    CATEGORY = "Easy Randomize"
    OUTPUT_NODE = True

    def record(self, **kwargs):
        texts = [kwargs.get(f"text_{i}", "") for i in range(1, 3) if kwargs.get(f"text_{i}")]
        result = json.dumps({"timestamp": datetime.now().isoformat(), "texts": texts})
        return (result,)


class SaveImageWithSelections(SaveImage):
    """SaveImage with selection metadata."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"})
            },
            "optional": {
                "selection_json": ("STRING", {"forceInput": True})
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    CATEGORY = "Easy Randomize"

    def save_images(self, images, filename_prefix="ComfyUI", selection_json=None, prompt=None, extra_pnginfo=None):
        if selection_json:
            if extra_pnginfo is None:
                extra_pnginfo = {}
            extra_pnginfo["selections"] = selection_json
        return super().save_images(images, filename_prefix, prompt, extra_pnginfo)


class SmartSelector:
    """Combined pool + selector with freeze functionality.

    Combines ItemPool, RandomSelector/SequentialSelector, and FreezableInput
    into a single node with mode-dependent options.

    When frozen=True: Uses the display widget value (ignores selection generation).
    When frozen=False: Generates selection based on mode, updates display widget.

    For sequential mode, the index widget auto-increments on each execution
    (unless frozen, which preserves the current position).

    Supports loading items from an external file via file_path parameter.
    When file_path is set, items are read from the file on each execution,
    allowing you to edit the file externally without modifying the workflow.

    The display widget stores the frozen value (persisted in workflow JSON).
    """

    @classmethod
    def IS_CHANGED(cls, use_file, items, file_path, mode, count,
                   allow_duplicates, index, wrap, frozen, display):
        """Force re-execution when not frozen to ensure fresh randomness/sequencing per queue item."""
        if frozen:
            # Frozen: allow caching (return stable value)
            return display
        # Not frozen: force re-execution for both random and sequential modes
        # Random needs new rolls; sequential needs index increment per batch item
        return float("nan")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Source toggle - controls whether to use items widget or file
                "use_file": ("BOOLEAN", {"default": False}),
                # Items widget (shown when use_file=False)
                "items": ("STRING", {"multiline": True, "default": "item1\nitem2\nitem3"}),
                # File path (shown when use_file=True)
                "file_path": ("STRING", {"default": ""}),
                # Mode selection
                "mode": (["random", "sequential"],),
                # Shared options
                "count": ("INT", {"default": 1, "min": 1, "max": 100}),
                # Random-only options
                "allow_duplicates": ("BOOLEAN", {"default": False}),
                # Sequential-only options
                "index": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "wrap": ("BOOLEAN", {"default": True}),
                # Freeze/display
                "frozen": ("BOOLEAN", {"default": False}),
                "display": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("selected", "item_count")
    FUNCTION = "select"
    OUTPUT_NODE = True
    CATEGORY = "Easy Randomize"

    def _parse_items(self, text):
        """Parse items from text, filtering out comments and empty lines.

        Supports both # and // style comments.
        """
        lines = text.strip().split('\n')
        parsed = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                parsed.append(stripped)
        return parsed

    def _load_items_from_file(self, file_path):
        """Load and parse items from a file.

        Returns (items_list, error_message). error_message is None on success.
        """
        if not file_path or not file_path.strip():
            return None, None  # No file specified, not an error

        file_path = file_path.strip()

        if not os.path.exists(file_path):
            return None, f"[File not found: {file_path}]"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_items(content), None
        except Exception as e:
            return None, f"[Error reading file: {e}]"

    def select(self, use_file, items, file_path, mode, count,
               allow_duplicates, index, wrap, frozen, display):
        # Load items based on use_file toggle
        if use_file:
            # Load from file
            file_items, file_error = self._load_items_from_file(file_path)
            if file_error:
                return {"ui": {"display": [file_error]}, "result": (file_error, 0)}
            if file_items is None:
                return {"ui": {"display": ["[No file path specified]"]}, "result": ("[No file path specified]", 0)}
            parsed_items = file_items
        else:
            # Parse from items widget
            parsed_items = self._parse_items(items)

        if not parsed_items:
            return {"ui": {"display": [""]}, "result": ("", 0)}

        item_count = len(parsed_items)

        # FROZEN: Use display widget value, don't update UI
        if frozen:
            result = display if display else ""
            return {"ui": {}, "result": (result, item_count)}

        # NOT FROZEN: Generate selection based on mode
        if mode == "random":
            # True randomness - no seed means different result each execution
            if allow_duplicates:
                selected = random.choices(parsed_items, k=min(count, len(parsed_items) * 100))
            else:
                selected = random.sample(parsed_items, k=min(count, len(parsed_items)))
            result = ", ".join(selected)
            return {"ui": {"display": [result]}, "result": (result, item_count)}

        else:  # sequential mode
            # Use widget value directly as current position
            current_pos = index

            selected = []
            for i in range(count):
                item_index = current_pos + i
                if wrap:
                    item_index = item_index % len(parsed_items)
                elif item_index >= len(parsed_items):
                    break
                selected.append(parsed_items[item_index])

            # Calculate next position for widget update
            next_pos = current_pos + count
            if wrap:
                next_pos = next_pos % len(parsed_items)

            result = ", ".join(selected)

            # Return with both display and index updates
            return {"ui": {"display": [result], "index": [next_pos]}, "result": (result, item_count)}


class PreviewImageWithText(SaveImage):
    """Preview image with a synced text display above it.

    The text widget only updates when the image updates (on execution).
    Useful for displaying prompts, labels, or metadata alongside previews.
    """

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                # Display widget - shows the text above the image
                "text_display": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                # Input text - connects from other nodes
                "text": ("STRING", {"forceInput": True}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "preview_with_text"
    OUTPUT_NODE = True
    CATEGORY = "Easy Randomize"

    def preview_with_text(self, images, text_display="", text=None, prompt=None, extra_pnginfo=None):
        # Use connected text input if available, otherwise use widget value
        display_text = text if text is not None else text_display

        # Call parent's save_images to handle the image preview
        result = self.save_images(images, prompt=prompt, extra_pnginfo=extra_pnginfo)

        # Add text_display to UI updates so the widget syncs with the image
        result["ui"]["text_display"] = [display_text]

        return result


# Node registration
NODE_CLASS_MAPPINGS = {
    "ItemPool": ItemPool,
    "RandomSelector": RandomSelector,
    "StringJoiner": StringJoiner,
    "FreezableInput": FreezableInput,
    "FreezableStringCombiner": FreezableStringCombiner,
    "TemplateFiller": TemplateFiller,
    "SelectionRecorder": SelectionRecorder,
    "SaveImageWithSelections": SaveImageWithSelections,
    "SmartSelector": SmartSelector,
    "PreviewImageWithText": PreviewImageWithText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ItemPool": "Item Pool",
    "RandomSelector": "Random Selector",
    "StringJoiner": "String Joiner",
    "FreezableInput": "Freezable Input",
    "FreezableStringCombiner": "Freezable String Combiner",
    "TemplateFiller": "Template Filler",
    "SelectionRecorder": "Selection Recorder",
    "SaveImageWithSelections": "Save Image (with Selections)",
    "SmartSelector": "Smart Selector 🎯",
    "PreviewImageWithText": "Preview Image + Text 📝",
}
