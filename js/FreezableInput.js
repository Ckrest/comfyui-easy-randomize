/**
 * Freezable Nodes Extension for ComfyUI
 * Updates display widgets after execution to show current/frozen values.
 */
import { app } from "/scripts/app.js";

// Helper to update widgets from UI message
function updateWidgetsFromMessage(node, message) {
    if (!message || !node.widgets) return;

    for (const [key, values] of Object.entries(message)) {
        if (Array.isArray(values) && values.length > 0) {
            const widget = node.widgets.find(w => w.name === key);
            if (widget) {
                const newValue = values[0];
                widget.value = newValue;
                // Trigger callback to update UI (important for INT/FLOAT widgets)
                if (widget.callback) {
                    widget.callback(newValue);
                }
            }
        }
    }

    // Trigger redraw
    if (node.setDirtyCanvas) {
        node.setDirtyCanvas(true, true);
    }
}

// FreezableInput - single input
app.registerExtension({
    name: "my_nodes.FreezableInput",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "FreezableInput") return;

        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (origOnExecuted) origOnExecuted.apply(this, arguments);
            updateWidgetsFromMessage(this, message);
        };
    },
});

// RandomSelector - update display widget after execution
app.registerExtension({
    name: "my_nodes.RandomSelector",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "RandomSelector") return;

        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (origOnExecuted) origOnExecuted.apply(this, arguments);
            updateWidgetsFromMessage(this, message);
        };
    },
});

// FreezableStringCombiner - 10 inputs with spacers between groups
app.registerExtension({
    name: "my_nodes.FreezableStringCombiner",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "FreezableStringCombiner") return;

        // Add visual spacers between slot groups for better organization
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            if (onNodeCreated) {
                onNodeCreated.apply(this, arguments);
            }

            // Store original widgets
            const originalWidgets = [...this.widgets];

            // Clear and rebuild with spacers
            this.widgets = [];

            for (const widget of originalWidgets) {
                this.widgets.push(widget);

                // Add spacer after each freeze_N toggle (but not freeze_all)
                if (widget.name.startsWith("freeze_") && widget.name !== "freeze_all") {
                    const spacerDiv = document.createElement("div");
                    spacerDiv.style.height = "10px";
                    spacerDiv.style.width = "100%";

                    const spacerWidget = this.addDOMWidget(
                        `spacer_${widget.name}`,
                        "div",
                        spacerDiv,
                        {
                            serialize: false,
                            hideOnZoom: false,
                        }
                    );
                    spacerWidget.computedHeight = 15;
                }
            }

            this.setSize(this.computeSize());
        };

        // Update widgets from Python's UI return
        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (origOnExecuted) origOnExecuted.apply(this, arguments);
            updateWidgetsFromMessage(this, message);
        };
    },
});

// SmartSelector - dynamic show/hide based on mode and use_file
app.registerExtension({
    name: "my_nodes.SmartSelector",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "SmartSelector") return;

        // Random-only widgets
        const randomWidgets = ["allow_duplicates"];
        // Sequential-only widgets
        const sequentialWidgets = ["index", "wrap"];

        // Function to update widget visibility based on mode (random vs sequential)
        const updateModeVisibility = function(mode) {
            if (!this.widgets) return;
            for (const widget of this.widgets) {
                if (randomWidgets.includes(widget.name)) {
                    widget.hidden = (mode !== "random");
                    if (widget.options) widget.options.hidden = (mode !== "random");
                }
                if (sequentialWidgets.includes(widget.name)) {
                    widget.hidden = (mode !== "sequential");
                    if (widget.options) widget.options.hidden = (mode !== "sequential");
                }
            }
        };

        // Function to update widget visibility based on use_file toggle
        const updateSourceVisibility = function(useFile) {
            if (!this.widgets) return;
            for (const widget of this.widgets) {
                if (widget.name === "items") {
                    // Show items widget when NOT using file
                    widget.hidden = useFile;
                    if (widget.options) widget.options.hidden = useFile;
                }
                if (widget.name === "file_path") {
                    // Show file_path widget when using file
                    widget.hidden = !useFile;
                    if (widget.options) widget.options.hidden = !useFile;
                }
            }
        };

        // Combined update function
        const updateAllVisibility = function() {
            const modeWidget = this.widgets?.find(w => w.name === "mode");
            const useFileWidget = this.widgets?.find(w => w.name === "use_file");

            if (modeWidget) updateModeVisibility.call(this, modeWidget.value);
            if (useFileWidget) updateSourceVisibility.call(this, useFileWidget.value);

            this.setSize(this.computeSize());
        };

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            if (onNodeCreated) {
                onNodeCreated.apply(this, arguments);
            }

            // Store update function on node for reuse
            this._updateAllVisibility = updateAllVisibility.bind(this);

            // Find mode widget and add callback
            const modeWidget = this.widgets.find(w => w.name === "mode");
            if (modeWidget) {
                const origCallback = modeWidget.callback;
                modeWidget.callback = (value) => {
                    if (origCallback) origCallback.call(this, value);
                    this._updateAllVisibility();
                };
            }

            // Find use_file widget and add callback
            const useFileWidget = this.widgets.find(w => w.name === "use_file");
            if (useFileWidget) {
                const origCallback = useFileWidget.callback;
                useFileWidget.callback = (value) => {
                    if (origCallback) origCallback.call(this, value);
                    this._updateAllVisibility();
                };
            }

            // Set initial visibility
            this._updateAllVisibility();
        };

        // Handle loading saved workflow - update visibility after values are restored
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function(info) {
            if (onConfigure) onConfigure.apply(this, arguments);

            // Update visibility based on loaded values
            if (this._updateAllVisibility) {
                this._updateAllVisibility();
            }
        };

        // Handle executed message - update display and index widgets
        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (origOnExecuted) origOnExecuted.apply(this, arguments);
            updateWidgetsFromMessage(this, message);
        };
    },
});

// WidgetTest - experimental node for testing MARKDOWN spacers
app.registerExtension({
    name: "my_nodes.WidgetTest",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "WidgetTest") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = async function() {
            if (onNodeCreated) {
                onNodeCreated.apply(this, arguments);
            }

            // Dynamically import ComfyWidgets
            const { ComfyWidgets } = await import("/scripts/widgets.js");

            // Store original widgets (text_1, text_2, text_3)
            const originalWidgets = [...this.widgets];

            // Clear widgets array to rebuild with spacers
            this.widgets = [];

            // Rebuild with spacers after each text input
            for (let i = 0; i < originalWidgets.length; i++) {
                // Add the original text widget
                this.widgets.push(originalWidgets[i]);

                // Create a simple div spacer with exact height control
                const spacerDiv = document.createElement("div");
                spacerDiv.style.height = "10px";
                spacerDiv.style.width = "100%";

                const spacerWidget = this.addDOMWidget(
                    `spacer_${i + 1}`,
                    "div",
                    spacerDiv,
                    {
                        serialize: false,
                        hideOnZoom: false,
                    }
                );
                spacerWidget.computedHeight = 15;
            }

            // Resize node to fit new widgets
            this.setSize(this.computeSize());
        };

        // Handle executed message - update spacer widgets
        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (origOnExecuted) origOnExecuted.apply(this, arguments);

            // Update spacer widgets with their corresponding text values
            for (let i = 1; i <= 3; i++) {
                const key = `spacer_${i}`;
                if (message?.[key]) {
                    const value = Array.isArray(message[key]) ? message[key][0] : message[key];
                    const widget = this.widgets?.find(w => w.name === key);
                    if (widget) widget.value = value;
                }
            }
        };
    },
});

// PreviewImageWithText - update text_display when image updates
app.registerExtension({
    name: "my_nodes.PreviewImageWithText",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "PreviewImageWithText") return;

        // Handle executed message - update text_display widget
        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (origOnExecuted) origOnExecuted.apply(this, arguments);
            updateWidgetsFromMessage(this, message);
        };
    },
});

// ListFilter - dynamic show/hide based on use_file toggle
app.registerExtension({
    name: "my_nodes.ListFilter",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "ListFilter") return;

        // Function to update widget visibility based on use_file toggle
        const updateSourceVisibility = function(useFile) {
            if (!this.widgets) return;
            for (const widget of this.widgets) {
                if (widget.name === "exclude_items") {
                    // Show exclude_items widget when NOT using file
                    widget.hidden = useFile;
                    if (widget.options) widget.options.hidden = useFile;
                }
                if (widget.name === "file_path") {
                    // Show file_path widget when using file
                    widget.hidden = !useFile;
                    if (widget.options) widget.options.hidden = !useFile;
                }
            }
        };

        const updateAllVisibility = function() {
            const useFileWidget = this.widgets?.find(w => w.name === "use_file");
            if (useFileWidget) updateSourceVisibility.call(this, useFileWidget.value);
            this.setSize(this.computeSize());
        };

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            if (onNodeCreated) {
                onNodeCreated.apply(this, arguments);
            }

            // Store update function on node for reuse
            this._updateAllVisibility = updateAllVisibility.bind(this);

            // Find use_file widget and add callback
            const useFileWidget = this.widgets.find(w => w.name === "use_file");
            if (useFileWidget) {
                const origCallback = useFileWidget.callback;
                useFileWidget.callback = (value) => {
                    if (origCallback) origCallback.call(this, value);
                    this._updateAllVisibility();
                };
            }

            // Set initial visibility
            this._updateAllVisibility();
        };

        // Handle loading saved workflow - update visibility after values are restored
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function(info) {
            if (onConfigure) onConfigure.apply(this, arguments);

            // Update visibility based on loaded values
            if (this._updateAllVisibility) {
                this._updateAllVisibility();
            }
        };

        // Handle executed message - update display widget
        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function(message) {
            if (origOnExecuted) origOnExecuted.apply(this, arguments);
            updateWidgetsFromMessage(this, message);
        };
    },
});

console.log("[Freezable Nodes] Extension loaded");
