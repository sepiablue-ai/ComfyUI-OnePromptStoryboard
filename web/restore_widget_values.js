// Restore explicit saved names after ComfyUI's positional-widget migration.
// Only our workflows carry this map; ordinary third-party workflows are untouched.
export function restoreNamedWidgetValues(node, data) {
    const saved = data?.widgets_values_named;
    if (!saved || typeof saved !== 'object' || Array.isArray(saved)) return;
    for (const widget of node.widgets ?? []) {
        if (!Object.prototype.hasOwnProperty.call(saved, widget.name)) continue;
        const value = saved[widget.name];
        if (value !== null && typeof value === 'object') continue;
        widget.value = value;
    }
}
