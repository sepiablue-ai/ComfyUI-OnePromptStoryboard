from .planning import DEFAULT_SYSTEM_PROMPT, build_system_prompt, parse_plan, compile_plan

WEB_DIRECTORY = './web'

class StoryboardPromptPlanner:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'clip':('CLIP',),
            'request':('STRING',{'multiline':True,'default':'黒髪お団子の成人女子大生が主人公の魔法少女の戦闘。14秒、4カット。夜の屋上、空中戦、崩れた広場、戦闘後の夜明けへ場面を切り替える。'}),
            'layout':(['横一列4コマ','縦一列4コマ'],),
            'seed':('INT',{'default':261026,'min':0,'max':0xffffffff})},
            'optional': {'system_prompt': ('STRING', {
                'multiline': True, 'default': DEFAULT_SYSTEM_PROMPT,
                'tooltip': '台本の演出方針を編集します。4カットのJSON出力形式はノードが末尾に付加します。Ollamaの設定は使用しません。'})}}
    RETURN_TYPES=('STRING','STRING','STRING','INT','INT')
    RETURN_NAMES=('MOSS用プロンプト','H3用プロンプト','共通台本','列数','行数')
    FUNCTION='plan'
    CATEGORY='ストーリーボード'
    DESCRIPTION='依頼文1つから接続した文章生成対応CLIPで共通台本を生成します。Qwen／Gemma等の対応モデルを選択でき、演出用システムプロンプトを編集できます。'

    def plan(self,clip,request,layout,seed,system_prompt=None):
        if not request.strip(): raise ValueError('作りたい動画の依頼文を入力してください。')
        from comfy_extras.nodes_textgen import TextGenerate
        result=TextGenerate.execute(clip=clip,prompt=request,max_length=1800,
            sampling_mode={'sampling_mode':'on','temperature':0.3,'top_k':20,'top_p':0.9,'min_p':0.0,'repetition_penalty':1.05,'seed':seed,'presence_penalty':0.0},
            thinking=False,use_default_template=True,mtp='off',system_prompt=build_system_prompt(system_prompt))
        text=result[0]
        try: outputs=compile_plan(parse_plan(text),layout)
        except ValueError as exc:
            raise ValueError(str(exc)+'\n生成された文章:\n'+str(text)) from exc
        return {'ui':{'text':[outputs[2]]},'result':outputs}

NODE_CLASS_MAPPINGS={'StoryboardPromptPlanner':StoryboardPromptPlanner}
NODE_DISPLAY_NAME_MAPPINGS={'StoryboardPromptPlanner':'① 作りたい動画をここに1つ入力'}


class StoryboardPromptText:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'text': ('STRING', {'multiline': True, 'default': ''})}}
    RETURN_TYPES = ('STRING',)
    RETURN_NAMES = ('H3用プロンプト',)
    FUNCTION = 'output_text'
    CATEGORY = 'ストーリーボード'
    def output_text(self, text):
        if not text.strip():
            raise ValueError('H3用プロンプトを入力してください。')
        return (text,)


class StoryboardPlanCompile:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'plan_json': ('STRING', {'multiline': True, 'default': ''}),
            'layout': (['横一列4コマ', '縦一列4コマ'],)}}
    RETURN_TYPES = ('STRING', 'STRING', 'STRING', 'INT', 'INT')
    RETURN_NAMES = StoryboardPromptPlanner.RETURN_NAMES
    FUNCTION = 'compile'
    CATEGORY = 'ストーリーボード'
    def compile(self, plan_json, layout):
        return compile_plan(parse_plan(plan_json), layout)


NODE_CLASS_MAPPINGS.update({
    'StoryboardPromptText': StoryboardPromptText,
    'StoryboardPlanCompile': StoryboardPlanCompile,
})
NODE_DISPLAY_NAME_MAPPINGS.update({
    'StoryboardPromptText': 'H3プロンプトを編集',
    'StoryboardPlanCompile': '保存済み共通台本から指示を復元',
})


class StoryboardOptionalLora:
    NONE = '（選択なし）'

    @classmethod
    def INPUT_TYPES(cls):
        import folder_paths
        return {'required': {
            'model': ('MODEL',),
            'prompt': ('STRING', {'forceInput': True}),
            'enabled': ('BOOLEAN', {'default': False}),
            'lora_name': ([cls.NONE] + folder_paths.get_filename_list('loras'),),
            'strength_model': ('FLOAT', {'default': 1.0, 'min': -100.0, 'max': 100.0, 'step': 0.05}),
            'trigger_words': ('STRING', {'default': '', 'multiline': True}),
        }}

    RETURN_TYPES = ('MODEL', 'STRING')
    RETURN_NAMES = ('MOSSモデル', 'MOSS用プロンプト')
    FUNCTION = 'apply'
    CATEGORY = 'ストーリーボード'
    DESCRIPTION = '初期OFFの任意LoRAとトリガーワード。MODELとSTRINGの両方を直列につなぎ、複製して追加できます。MOSS用LoRAを選択してください。'

    def apply(self, model, prompt, enabled=False, lora_name=NONE, strength_model=1.0, trigger_words=''):
        if not enabled:
            return (model, prompt)
        if lora_name != self.NONE and strength_model != 0:
            from nodes import LoraLoaderModelOnly
            model = LoraLoaderModelOnly().load_lora_model_only(model, lora_name, strength_model)[0]
        words = trigger_words.strip()
        if words:
            prompt = words + '\n' + prompt
        return (model, prompt)


NODE_CLASS_MAPPINGS['StoryboardOptionalLora'] = StoryboardOptionalLora
NODE_DISPLAY_NAME_MAPPINGS['StoryboardOptionalLora'] = '任意LoRA＋トリガーワード（初期OFF）'
