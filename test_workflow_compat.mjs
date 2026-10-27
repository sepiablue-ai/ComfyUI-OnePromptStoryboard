import assert from 'node:assert/strict';
import { restoreNamedWidgetValues } from './web/restore_widget_values.js';

const node = { widgets: [
    { name: 'panels', value: 496 }, { name: 'panel_edge', value: 8 },
    { name: 'margin', value: 'object' }, { name: 'reborder', value: true },
    { name: 'shave', value: '' }, { name: 'unrelated', value: 42 },
] };
restoreNamedWidgetValues(node, { widgets_values_named: {
    panels: 4, panel_edge: 640, margin: 8, reborder: false, shave: 0,
} });
assert.deepEqual(node.widgets.map(w => w.value), [4, 640, 8, false, 0, 42]);
const ordinary = { widgets: [{ name: 'panels', value: 9 }] };
restoreNamedWidgetValues(ordinary, { widgets_values: [4] });
assert.equal(ordinary.widgets[0].value, 9);
console.log('項目名による値復元と、対象外ワークフローを変更しないことを確認しました。');
