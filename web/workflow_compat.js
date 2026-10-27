import { app } from '../../scripts/app.js';
import { restoreNamedWidgetValues } from './restore_widget_values.js';

app.registerExtension({
    name: 'OnePromptStoryboard.NamedWidgetValues',
    nodeCreated(node) {
        const original = node.onConfigure;
        node.onConfigure = function (data) {
            const result = original?.apply(this, arguments);
            restoreNamedWidgetValues(this, data);
            return result;
        };
    },
});
