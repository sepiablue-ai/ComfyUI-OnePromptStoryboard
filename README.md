# ComfyUI-OnePromptStoryboard

通常版はMOSSと共通のQwen3.5を使用し、キャラ・画風などの追加LoRAは初期OFFです。Gemma4への切替、システムプロンプト編集、任意LoRAの使い方は[モデル選択と設定](docs/GEMMA4_DEVELOPMENT.md)を参照してください。

依頼文1つから4カットの共通台本を作り、MOSS用のストーリーボード指示とMiniMax H3 Ref2VA用の動画指示に変換するComfyUIカスタムノードです。

**このrepoで導入するのは自作ノードだけです。モデル、MOSS／H3本体、外部カスタムノード、Pythonパッケージを自動インストールしません。** 非公式の補助ノードです。

## インストール

ComfyUIの `custom_nodes` フォルダーで実行し、ComfyUIを再起動してください。

```sh
git clone https://github.com/sepiablue-ai/ComfyUI-OnePromptStoryboard.git
```

ZIPを展開して `custom_nodes/ComfyUI-OnePromptStoryboard` に置く方法でも導入できます。ノード登録自体に追加のpip依存はありません。

## ノード

| 登録名 | 用途 |
| --- | --- |
| `StoryboardPromptPlanner` | 依頼文と既存CLIPから共通台本を作成。通常版はQwen3.5、任意でGemma4を利用。MOSS指示・H3指示・台本JSON・列数・行数を出力 |
| `StoryboardPromptText` | H3プロンプトを手で編集して出力。モデル不要 |
| `StoryboardPlanCompile` | 保存済み台本JSONから両モデルの指示を復元。LLMの再実行不要 |
| `StoryboardOptionalLora` | MOSS用の追加LoRAとトリガーワード。初期OFF、複製して直列に追加可能 |

プランナーはComfyUI標準の `comfy_extras.nodes_textgen.TextGenerate` を使用します。このAPIおよびMOSS／H3ネイティブ機能を持つComfyUIが必要です。古いComfyUIでは更新が必要になる場合があります。単にノード名が存在するだけで任意のCLIPが文章生成できるわけではありません。付属例は `moss_image` のQwen3.5 9Bエンコーダーを使います。

## 別途必要なもの

一括生成の例では次を利用者自身で導入してください。各プロジェクトの手順とライセンスに従ってください。

- MOSS／MiniMax H3／Ref2VA／BlockSparseAttention／TextGenerate対応の [ComfyUI](https://github.com/Comfy-Org/ComfyUI)
- [ComfyUI-MOSS-Storyboard](https://github.com/ZenHG/ComfyUI-MOSS-Storyboard)：`MossStoryboardSampler` と `MossStoryboardLayout`
- [ComfyUI-FastH3-OmniRef-Accel](https://github.com/sepiablue-ai/ComfyUI-FastH3-OmniRef-Accel)：付属例のH3高速化・LBH・動画保存用。LBH潜在アップスケーラー等の導入条件も同repoで確認してください
- 動画保存用のNVIDIA NVENC対応環境と、FastH3側が必要とするFFmpeg等

**H3のみの例ではMOSSとそのモデルは不要です。** プロンプト編集ノード自身はQwenも不要です。FastH3側の必要条件は残ります。

### 付属例で指定しているモデル

| ファイル名 | ComfyUI内の配置先 |
| --- | --- |
| `moss_image_sft_int8_convrot.safetensors` | `models/diffusion_models` |
| `lora.safetensors`（SFT用8step DMD） | `models/loras` |
| `qwen3.5_9b_int8_convrot.safetensors` | `models/text_encoders` |
| `flux2-vae.safetensors` | `models/vae` |
| `fasth3_omniref_8step_pruned_int8_convrot.safetensors` | `models/diffusion_models` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `models/text_encoders` |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `models/vae` |
| `minimax_h3_audio_vae_fp32.safetensors` | `models/vae` |
| `minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors` | `models/latent_upscale_models` |
| `realesr-animevideov3.pth` | `models/upscale_models` |

H3モデルの配布元は [FastVideo/FastH3-Omni-Comfy](https://huggingface.co/FastVideo/FastH3-Omni-Comfy)。H3・LBH・Real-ESRGANの導入条件はFastH3 repoの手順も参照してください。ファイルは配布名のまま使用します。サブフォルダーへ置いた場合はワークフローの選択欄を合わせてください。独自の画風LoRAは同梱せず、付属例でも必須にしていません。

MOSSのSFT INT8本体・Qwen・VAEは [Comfy-Org/MOSS-Image](https://huggingface.co/Comfy-Org/MOSS-Image/tree/main) で配布されています。蒸留LoRAは [lodestones/MOSS-Image-SFT-8-steps-dmd](https://huggingface.co/lodestones/MOSS-Image-SFT-8-steps-dmd) の [`lora.safetensors`](https://huggingface.co/lodestones/MOSS-Image-SFT-8-steps-dmd/blob/main/lora.safetensors) を名前を変えずに使用します。`lora_latest.safetensors` は別の重みです。Base用DMD LoRAとも区別してください。

LBHは [Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/tree/main/minimax_h3_latent_upscaler_3d_conv_v1) 内の `minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors` を名前を変えずに使用します。ワークフローも配布名に統一しました。

### 配布物との一致確認と精度について

2026-10-26に、検証環境の重みと配布元のLFS SHA-256を照合しました。

| 配布ファイル | SHA-256 |
| --- | --- |
| SFT DMD `lora.safetensors` | `4abb14e39c1a59018907581e609f43616ec6810126144ec2b1d2e6f8969628fe` |
| LBH `minimax_h3_latent_upscaler_3d_conv_v1_fp16.safetensors` | `043e5a48e161610ef6c3ea974645220354d06fa618abca15f76d084812eb55c2` |

lodestonesの現行モデルカードは、通常のComfyUI LoRAローダーで `lora.safetensors` を強度1で使う手順を示しています。一方、下部の「Deprecated」と明記された旧 `transformer/` 方式では、蒸留差分がBF16丸めより小さいためFP32での読み込み・実行が必要、と説明しています。この旧方式の要件を、現行LoRA利用時も本体のFP32化が必須という意味には扱っていません。本repoの例はINT8本体＋別適用LoRAで、配布元のFP32構成との品質比較は未実施です。精度や適用方法によって品質が変わる可能性はあります。

## 文章1つから一括生成

最初は `workflows/all_in_one_magic_battle.json` をComfyUIへ読み込んでください。QwenをMOSSと共用する通常版です。恋愛・出会いの通常例もQwenです。`.api.json` はAPI送信用です。

`all_in_one_magic_battle_gemma4.json` は別モデルを用意する任意サンプルで、Gemma4が初期選択されています。通常版にGemma4のダウンロードやOllamaは不要です。

1. 「① 作りたい動画をここに1つ入力」の依頼文を書き換えます。
2. 横一列4コマ／縦一列4コマを選び、モデルの選択欄を確認します。
3. 実行します。依頼文→共通台本→MOSS画像→その画像1枚をH3へ参照入力→動画保存の順に処理します。
4. 気に入ったら、保存されたストーリーボードに加え、「保存用・生成されたH3プロンプト」「自動生成した共通台本」のプレビューをコピーしてテキスト保存してください。台本・プロンプトのファイル自動保存は実装していません。

例は魔法少女の戦闘、ボーイミーツガール、恋愛映画の3種類です。人が書く物語の文章は1つで、各モデルへの指示は自動生成します。4カット・約14秒を前提とし、任意のコマ数には対応していません。

## システムプロンプトと追加LoRA

依頼文ノードの `system_prompt` で、台本の演出方針を変えられます。通常の物語は `request` に1つ入力するだけです。必要な4カットJSONの形式指定はノードが付加します。

任意LoRAのエリアには初期OFFの枠が3つあります。使う枠でMOSS用LoRA、`strength_model`、`trigger_words` を指定し、`enabled` をONにしてください。トリガーはMOSS用プロンプトへ直接追加されます。OFF時はLoRAをロードせず、トリガーも追加しません。枠を増やす場合はノードを複製し、MODELとSTRINGの両方を直列につなぎます。

キャラ・画風LoRAは同梱・自動取得しません。初期状態では不要です。8step生成に必要なSFT用DMD `lora.safetensors` は任意エリアの手前で有効であり、別途必要です。

更新後はComfyUIを再起動し、ブラウザーを強制再読み込みしてrepoの元JSONを読み直してください。エリア分けと設定値の名前による復元が含まれます。

## 良いストーリーボードを固定し、H3だけ作り直す

`workflows/h3_from_saved_storyboard.json` を読み込みます。

1. 「保存済みストーリーボードを1枚選択」で実際に使う画像を読み込みます。`storyboard.png` は仮のファイル名です。
2. 「H3プロンプトを編集」に、その画像とセットで保存したH3プロンプトを貼り付けます。初期値は横4コマの魔法少女の例なので、別の画像には必ず書き換えてください。
3. コマの順序、人物や衣装の対応は保ち、動作・カメラ・音などを調整します。縦4コマなら上下順への対応も変更してください。
4. 実行します。このグラフにはMOSSや台本生成への接続がなく、H3だけを実行します。

台本JSONしか保存していない場合は、`StoryboardPlanCompile` に台本を貼り付け、元と同じ配置を選んでH3指示を復元できます。復元した出力をプレビューして編集欄へコピーすれば、その後は台本生成なしで変更できます。

## 参照の仕組みと制限

Qwenは生成後の画像を見ません。共通台本の静止画構図をMOSSへ、動作やカメラを含む指示をH3へ渡します。「参照画像1は4コマ、各コマがショット1〜4に対応、枠を除いた全画面映像へ展開」という規則は固定テンプレートです。FL2VA用にコマを切り分けず、MOSSの全体画像の出力0をRef2VAへ1枚接続します。

MOSSがコマ数や内容を守らなかった場合に、自動検出・補正する機能はありません。任意レイアウトの画像解析、文字説明の自動読取も行いません。不正な台本JSONや4カット不足はエラーで停止します。BGM出力欄は現在 `N/A` 固定で、依頼した音楽をH3へ反映する機能は未対応です。

MOSSの `reborder=false` とし、生成後の枠線描き直しは無効です。付属H3例はFastH3側のLBH潜在拡大、Real-ESRGAN、リサイズ・中央切り抜き、NVENC保存を利用します。本repo自身は画像・動画の補修や合成をしません。

## 検証

2026-10-27、通常一括版をQwen共用・追加LoRA全OFF・システムプロンプトとseedも初期値のまま実行し、画像と動画を保存できました（203.80秒）。その保存画像と対応するH3プロンプトをH3のみの例へ入力した実行も成功しました（173.04秒）。

両方とも1024×1792・24fps・14.375秒、映像345フレームと音声450フレームを最後までデコードできました。今回は2本の動画ファイルのSHA-256も一致しました。詳細と検証範囲は[通常版の実行確認](docs/DEFAULT_VALIDATION.md)を参照してください。

新規cloneしたコードの単体テスト16件と、フロントエンドの設定値復元テストが成功しました。今回の実生成はAPI経由で、GUIの接続・名前付き設定は静的照合しています。追加モデルなしのテストは次で実行できます。

```sh
python -m unittest discover -p "test_*.py" -v
```

これ以前の独立環境での導入確認は[旧版の検証記録](docs/VALIDATION.md)、GemmaとGUI値復元の確認は[モデル選択と設定](docs/GEMMA4_DEVELOPMENT.md)に記載しています。実行成功は映像の品質やすべての環境での動作を保証するものではありません。

## ライセンス

GPL-3.0。H3例はGPL-3.0の [ComfyUI-FastH3-OmniRef-Accel](https://github.com/sepiablue-ai/ComfyUI-FastH3-OmniRef-Accel) のワークフローを基にしています。モデル・外部ノードは各々のライセンスが適用されます。モデルや外部実装は同梱しません。
