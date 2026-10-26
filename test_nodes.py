import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location('storyboard_test_package', ROOT / '__init__.py', submodule_search_locations=[str(ROOT)])
nodes = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nodes
spec.loader.exec_module(nodes)


class NodeTests(unittest.TestCase):
    def test_text_preserved_and_empty_rejected(self):
        node = nodes.StoryboardPromptText()
        self.assertEqual(node.output_text('Reference\nShot 1'), ('Reference\nShot 1',))
        with self.assertRaises(ValueError): node.output_text('  ')

    def test_saved_plan_without_llm(self):
        plan = {'title': '検証', 'summary': 'Four scenes', 'hero': 'Adult', 'support': '', 'style': 'Anime',
                'shots': [dict(scene=str(i), keyframe='Standing', action='Walks', camera='Static', sound='Wind') for i in range(4)]}
        result = nodes.StoryboardPlanCompile().compile(json.dumps(plan), '縦一列4コマ')
        self.assertEqual(result[3:], (1, 4))
        self.assertIn('top, second from the top', result[1])
        self.assertNotIn('qsv2style', result[0])

    def test_h3_only_has_no_moss_or_llm_ancestors(self):
        graph = json.loads((ROOT / 'workflows/h3_from_saved_storyboard.api.json').read_text(encoding='utf-8'))
        self.assertEqual(graph['209']['inputs']['ref_images.ref_image_0'], ['206', 0])
        self.assertEqual(graph['209']['inputs']['prompt'], ['303', 0])
        types = {n['class_type'] for n in graph.values()}
        self.assertFalse(types & {'MossStoryboardSampler', 'StoryboardPromptPlanner', 'StoryboardPlanCompile'})
        self.assertFalse(any('moss' in str(n).lower() for n in graph.values()))

    def test_all_in_one_single_image_and_no_personal_lora(self):
        for path in (ROOT / 'workflows').glob('all_in_one_*.api.json'):
            graph = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(graph['209']['inputs']['ref_images.ref_image_0'], ['105', 0])
            self.assertEqual(graph['209']['inputs']['prompt'], ['301', 1])
            self.assertEqual(graph['105']['inputs']['positive'], ['301', 0])
            self.assertFalse(graph['105']['inputs']['reborder'])
            self.assertNotIn('SepiaBlue', str(graph))

    def test_all_graph_edges_resolve(self):
        for path in (ROOT / 'workflows').glob('*.api.json'):
            graph = json.loads(path.read_text(encoding='utf-8'))
            for node in graph.values():
                for val in node['inputs'].values():
                    if isinstance(val, list): self.assertIn(val[0], graph, str(path))


if __name__ == '__main__': unittest.main()
