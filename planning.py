"""Strict plan validation and text-only compilation. No media postprocessing."""
import json

SYSTEM_PROMPT = '''You are a film storyboard planner. Convert the user's Japanese or English request into one compact four-shot plan for a 14-second anime video. Translate the plan content to English, except title which must be Japanese. Respect the user's characters, genre and story. Default protagonist only if unspecified: an adult university woman with black hair in one high bun. All romantic characters are adults. The same cast must remain recognizable. Each of the FOUR shots must be a different dramatic scene, with a clearly changed location and/or time, not nearby angles of one continuous event. Do not invent dialogue or music unless requested. A still keyframe describes the visible initial pose; action describes the movement after it. Keep the complete JSON concise, preferably under 600 English words. Output ONLY one valid JSON object, no thinking, Markdown or preface, with exactly this structure:
{"title":"日本語の題名","summary":"English story summary","hero":"Main protagonist identity, age, hair, outfit","support":"Other recurring characters or important props; empty string if none","style":"Visual rendering and cinematography","shots":[{"scene":"Distinct location, time, lighting","keyframe":"Composition, initial pose, visible subjects and props","action":"Concrete movement and outcome for this shot","camera":"Simple coherent camera movement","sound":"Ambience and action sounds"},{"scene":"...","keyframe":"...","action":"...","camera":"...","sound":"..."},{"scene":"...","keyframe":"...","action":"...","camera":"...","sound":"..."},{"scene":"...","keyframe":"...","action":"...","camera":"...","sound":"..."}]}
Exactly four shots. Do not insert example ellipses in the actual output.'''

def parse_plan(text):
    text=text.strip()
    if text.startswith('```'):
        lines=text.splitlines()
        if lines[-1].strip()=='```': text='\n'.join(lines[1:-1]).strip()
    try: plan=json.loads(text)
    except (ValueError,TypeError) as exc:
        raise ValueError('共通台本が有効なJSONになりませんでした。生成文を確認してください。') from exc
    if not isinstance(plan,dict): raise ValueError('共通台本はJSONオブジェクトである必要があります。')
    for key in ('title','summary','hero','support','style'):
        if not isinstance(plan.get(key),str) or (key!='support' and not plan[key].strip()):
            raise ValueError(f'共通台本の項目が不足しています: {key}')
    if not isinstance(plan.get('shots'),list) or len(plan['shots'])!=4:
        raise ValueError('共通台本には4カットが必要です。途中で省略された台本は使用しません。')
    for i,shot in enumerate(plan['shots'],1):
        if not isinstance(shot,dict): raise ValueError(f'カット{i}の形式が不正です。')
        for key in ('scene','keyframe','action','camera','sound'):
            if not isinstance(shot.get(key),str) or not shot[key].strip():
                raise ValueError(f'カット{i}の項目が不足しています: {key}')
    return plan

def compile_plan(plan,layout):
    # Validate even plans supplied directly by another caller.
    plan=parse_plan(json.dumps(plan,ensure_ascii=False))
    if layout=='横一列4コマ':
        cols,rows=4,1
        direction='one horizontal row, read left to right'
        positions=['leftmost','second from the left','third from the left','rightmost']
    elif layout=='縦一列4コマ':
        cols,rows=1,4
        direction='one vertical column, read top to bottom'
        positions=['top','second from the top','third from the top','bottom']
    else: raise ValueError('未対応のストーリーボード配置です。')
    moss=(f'Detailed anime illustration. {plan["style"]}. '
          f'A single storyboard sheet with exactly FOUR equal square panels in {direction}. '
          'Thin white dividers. No captions, numbers, speech bubbles or writing. '
          f'Consistent main protagonist: {plan["hero"]}. Recurring cast and props: {plan["support"]}. '
          'Every panel represents a different dramatic scene, with a changed place and/or time. '
          'Keep faces and important gestures readable.\n')
    for i,shot in enumerate(plan['shots']):
        moss+=f'[PANEL {i+1}]: {positions[i]} panel. {shot["scene"]}. {shot["keyframe"]}.\n'
    h3=(f'subject_definitions:\n<Picture 1> is the complete four-panel storyboard; its '
        f'{", ".join(positions)} panels map to [Shot 1] through [Shot 4], respectively.\n'
        f'<Subject 1> is the main protagonist in <Picture 1>: {plan["hero"]}.\n'
        f'<Subject 2> comprises the recurring cast and props in <Picture 1>: {plan["support"] or "only the protagonist and depicted scene objects"}.\n\n'
        f'summary:\n[reference generation] A 14-second four-shot anime montage. {plan["summary"]} '
        'Use the single storyboard as the visual reference and follow the actions below.\n\n'
        'retention_analysis:\n<Picture 1> (all four shots): fully_preserved - retain each panel\'s scene, composition and order as successive full-screen shots; dividers are planning marks.\n'
        '<Subject 1> (all four shots): fully_preserved - retain identity, hair and the depicted clothing.\n'
        '<Subject 2> (where present in the panels): fully_preserved - retain the depicted appearances and roles.\n\n'
        f'detailed_description:\n{plan["style"]}. Match the luminous rendering of <Picture 1>. '
        'Show exactly one full-frame scene at a time. No storyboard sheet, panel grid, repeated panels, borders, captions or writing. '
        'Hard cut to a distinctly different place/time/situation for every new shot, without morphing the locations together.\n')
    for i,shot in enumerate(plan['shots']):
        lead='[Shot 1] ' if i==0 else f'[Shot {i+1}] At 00:{i*3.5:06.3f}, hard cut. '
        h3+=(lead+f'The scene follows the {positions[i]} panel of <Picture 1>. {shot["scene"]}. '
             f'{shot["keyframe"]}. Animate the action: {shot["action"]}. '
             f'Camera: {shot["camera"]}. Synchronized sound: {shot["sound"]}.\n')
    h3+='\noverall_soundscape:\n'+' '.join(f'Shot {i+1}: {s["sound"]}.' for i,s in enumerate(plan['shots']))
    h3+='\n\nnon_diegetic_music:\nN/A\n'
    return moss,h3,json.dumps(plan,ensure_ascii=False,indent=2),cols,rows
