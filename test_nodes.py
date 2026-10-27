import importlib.util
import json
from pathlib import Path
import sys
import unittest
from types import ModuleType
from unittest.mock import patch

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location('storyboard_test_package', ROOT / '__init__.py', submodule_search_locations=[str(ROOT)])
nodes = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nodes
spec.loader.exec_module(nodes)


class NodeTests(unittest.TestCase):
    def test_custom_policy_and_fixed_contract_reach_text_generate(self):
        plan = {'title': '検証', 'summary': 'Four scenes', 'hero': 'Adult', 'support': '', 'style': 'Anime',
                'shots': [dict(scene=str(i), keyframe='Standing', action='Walks', camera='Static', sound='Wind') for i in range(4)]}
        received = {}
        class TextGenerate:
            @staticmethod
            def execute(**kwargs):
                received.update(kwargs)
                return (json.dumps(plan), '')
        parent = ModuleType('comfy_extras')
        module = ModuleType('comfy_extras.nodes_textgen')
        module.TextGenerate = TextGenerate
        clip = object()
        with patch.dict(sys.modules, {'comfy_extras': parent, 'comfy_extras.nodes_textgen': module}):
            nodes.StoryboardPromptPlanner().plan(clip, '依頼', '横一列4コマ', 1, 'All cameras must be static.')
        self.assertIs(received['clip'], clip)
        self.assertIn('All cameras must be static.', received['system_prompt'])
        self.assertIn('Exactly four shots.', received['system_prompt'])
        self.assertIn('"shots"', received['system_prompt'])
        self.assertFalse(received['thinking'])

    def test_default_system_prompt_backwards_compatible(self):
        from storyboard_test_package.planning import SYSTEM_PROMPT, build_system_prompt
        self.assertEqual(build_system_prompt(), SYSTEM_PROMPT)

    def test_gemma_planner_is_separate_from_moss_encoder(self):
        graph = json.loads((ROOT / 'workflows/all_in_one_magic_battle_gemma4.api.json').read_text(encoding='utf-8'))
        self.assertEqual(graph['301']['inputs']['clip'], ['306', 0])
        self.assertEqual(graph['105']['inputs']['clip'], ['103', 0])
        self.assertEqual(graph['306']['inputs']['clip_name'], 'gemma4_e4b_it_int8_convrot.safetensors')
        self.assertEqual(graph['103']['inputs']['clip_name'], 'qwen3.5_9b_int8_convrot.safetensors')

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
            self.assertEqual(graph['105']['inputs']['positive'], ['309', 1])
            self.assertEqual(graph['105']['inputs']['model'], ['309', 0])
            for nid, previous in [('307', '102'), ('308', '307'), ('309', '308')]:
                self.assertEqual(graph[nid]['inputs']['model'], [previous, 0])
                self.assertFalse(graph[nid]['inputs']['enabled'])
                self.assertEqual(graph[nid]['inputs']['lora_name'], nodes.StoryboardOptionalLora.NONE)
            self.assertEqual(graph['307']['inputs']['prompt'], ['301', 0])
            self.assertFalse(graph['105']['inputs']['reborder'])
            self.assertNotIn('SepiaBlue', str(graph))

    def test_disabled_optional_lora_does_not_load_or_add_trigger(self):
        model = object()
        result = nodes.StoryboardOptionalLora().apply(model, 'original', False, 'missing.safetensors', 1, 'trigger')
        self.assertIs(result[0], model)
        self.assertEqual(result[1], 'original')

    def test_multiple_loras_and_triggers_are_chained(self):
        calls = []
        module = ModuleType('nodes')
        class Loader:
            def load_lora_model_only(self, model, name, strength):
                calls.append((model, name, strength))
                return (model + '/' + name,)
        module.LoraLoaderModelOnly = Loader
        with patch.dict(sys.modules, {'nodes': module}):
            block = nodes.StoryboardOptionalLora()
            model, prompt = block.apply('base', 'original', True, 'character.safetensors', 0.7, 'character_trigger')
            model, prompt = block.apply(model, prompt, True, 'style.safetensors', 0.8, 'style_trigger')
        self.assertEqual(model, 'base/character.safetensors/style.safetensors')
        self.assertEqual(len(calls), 2)
        self.assertIn('character_trigger', prompt)
        self.assertIn('style_trigger', prompt)
        self.assertTrue(prompt.endswith('original'))

    def test_trigger_only_without_lora_file(self):
        model = object()
        result = nodes.StoryboardOptionalLora().apply(model, 'original', True, trigger_words='  trigger  ')
        self.assertIs(result[0], model)
        self.assertEqual(result[1], 'trigger\noriginal')

    def test_all_graph_edges_resolve(self):
        for path in (ROOT / 'workflows').glob('*.api.json'):
            graph = json.loads(path.read_text(encoding='utf-8'))
            for node in graph.values():
                for val in node['inputs'].values():
                    if isinstance(val, list): self.assertIn(val[0], graph, str(path))


if __name__ == '__main__': unittest.main()
