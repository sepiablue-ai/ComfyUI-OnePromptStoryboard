import copy,json,unittest
from planning import parse_plan,compile_plan

class PlanTests(unittest.TestCase):
    def setUp(self):
        self.p={'title':'テスト','summary':'Four scenes','hero':'Adult woman','support':'','style':'Anime',
            'shots':[{'scene':f'Location {i}','keyframe':'Standing','action':f'Action {i}','camera':'Slow push','sound':'Wind'} for i in range(4)]}
    def test_shared_actions_and_single_picture(self):
        m,h,p,c,r=compile_plan(self.p,'横一列4コマ')
        self.assertEqual((c,r),(4,1)); self.assertEqual(m.count('[PANEL '),4)
        self.assertIn('Action 3',h); self.assertNotIn('<Picture 2>',h)
        self.assertIn('[Shot 4] At 00:10.500',h); self.assertEqual(json.loads(p),self.p)
    def test_vertical_mapping(self):
        m,h,p,c,r=compile_plan(self.p,'縦一列4コマ')
        self.assertEqual((c,r),(1,4)); self.assertIn('bottom panel',h)
    def test_truncated_plan_rejected(self):
        self.p['shots'].pop()
        with self.assertRaisesRegex(ValueError,'4カット'): parse_plan(json.dumps(self.p))
    def test_missing_action_rejected(self):
        self.p['shots'][1]['action']=''
        with self.assertRaisesRegex(ValueError,'action'): compile_plan(self.p,'横一列4コマ')
    def test_fenced_json_is_data_not_code(self):
        self.assertEqual(parse_plan('```json\n'+json.dumps(self.p)+'\n```'),self.p)
        with self.assertRaises(ValueError): parse_plan('__import__("os")')

if __name__=='__main__': unittest.main()
