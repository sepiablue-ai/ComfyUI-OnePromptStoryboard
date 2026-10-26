# ComfyUI-OnePromptStoryboard

依頼文1つから4カットの共通台本を作り、MOSS用のストーリーボード指示とMiniMax H3 Ref2VA用の動画指示に変換するComfyUIカスタムノードです。

**このrepoで導入するのは自作ノードだけです。モデル、MOSS／H3本体、外部カスタムノード、Pythonパッケージを自動インストールしません。** 非公式の補助ノードです。

## インストール

ComfyUIの `custom_nodes` フォルダーで実行し、ComfyUIを再起動してください。

```sh
git clone https://github.com/sepiablue-ai/ComfyUI-OnePromptStoryboard.git
```

非公開repoのため、招待済みGitHubアカウントの認証が必要です。ZIPを展開して `custom_nodes/ComfyUI-OnePromptStoryboard` に置く方法でも導入できます。ノード登録自体に追加のpip依存はありません。

## ノード

| 登録名 | 用途 |
| --- | --- |
| `StoryboardPromptPlanner` | 依頼文と既存CLIPからローカルQwen3.5で共通台本を作り、MOSS指示・H3指示・台本JSON・列数・行数を出力 |
| `StoryboardPromptText` | H3プロンプトを手で編集して出力。モデル不要 |
| `StoryboardPlanCompile` | 保存済み台本JSONから両モデルの指示を復元。LLMの再実行不要 |

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
| `moss_image_sft_8step_dmd.safetensors` | `models/loras` |
| `qwen3.5_9b_int8_convrot.safetensors` | `models/text_encoders` |
| `flux2-vae.safetensors` | `models/vae` |
| `fasth3_omniref_8step_pruned_int8_convrot.safetensors` | `models/diffusion_models` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `models/text_encoders` |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `models/vae` |
| `minimax_h3_audio_vae_fp32.safetensors` | `models/vae` |
| `minimax_h3_latent_upscaler_3d_fp16.safetensors` | `models/latent_upscale_models` |
| `realesr-animevideov3.pth` | `models/upscale_models` |

H3モデルの配布元は [FastVideo/FastH3-Omni-Comfy](https://huggingface.co/FastVideo/FastH3-Omni-Comfy)。MOSS導入例は [moss-image-workflows](https://github.com/sepiablue-ai/moss-image-workflows)、H3・LBH・Real-ESRGANの導入はFastH3 repoの手順を参照してください。ダウンロード済みのファイル名やサブフォルダーに合わせ、ワークフローの選択欄を変更してください。独自の画風LoRAは同梱せず、付属例でも必須にしていません。

## 文章1つから一括生成

`workflows/all_in_one_*.json` のいずれかをComfyUIへ読み込みます。`.api.json` はAPI送信用です。

1. 「① 作りたい動画をここに1つ入力」の依頼文を書き換えます。
2. 横一列4コマ／縦一列4コマを選び、モデルの選択欄を確認します。
3. 実行します。依頼文→共通台本→MOSS画像→その画像1枚をH3へ参照入力→動画保存の順に処理します。
4. 気に入ったら、保存されたストーリーボードに加え、「保存用・生成されたH3プロンプト」「自動生成した共通台本」のプレビューをコピーしてテキスト保存してください。台本・プロンプトのファイル自動保存は実装していません。

例は魔法少女の戦闘、ボーイミーツガール、恋愛映画の3種類です。人が書く物語の文章は1つで、各モデルへの指示は自動生成します。4カット・約14秒を前提とし、任意のコマ数には対応していません。

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

基になった画風LoRA付き一括版はRTX 4070で動画保存まで202.14秒、1024×1792、24fps、345フレーム、14.375秒でした。これは当時の構成での実測で、配布版のLoRAなしの速度・品質を保証する値ではありません。発光で顔が隠れる、画角から顔が外れる等の品質課題があります。

配布版は新規専用venvと公式ComfyUIから構築した独立環境でも、一括生成（207.51秒）と保存済み画像を固定したH3のみの生成（170.29秒）が成功しました。画風LoRAは使っていません。両方とも14.375秒・345フレームの映像と音声を最後までデコードできました。詳しくは [独立環境での検証](docs/VALIDATION.md) を参照してください。

4種類の画面用/API用グラフの接続・設定対応、台本処理・ノード・保存済み画像経路のテスト10件も成功しています。実生成はAPI形式で行い、画面への読み込み操作は未検証です。テストは追加モデルなしで実行できます。

```sh
python -m unittest discover -p "test_*.py" -v
```

## ライセンス

GPL-3.0。H3例はGPL-3.0の [ComfyUI-FastH3-OmniRef-Accel](https://github.com/sepiablue-ai/ComfyUI-FastH3-OmniRef-Accel) のワークフローを基にしています。モデル・外部ノードは各々のライセンスが適用されます。モデルや外部実装は同梱しません。
