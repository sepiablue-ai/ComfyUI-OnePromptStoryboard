# Gemma4・システムプロンプト編集の開発版

開発ブランチ：`dev/gemma4-planner`。mainへはまだ統合していません。

## 接続とモデル選択

`workflows/all_in_one_magic_battle_gemma4.json` を読み込みます。「台本用モデル・Qwen／Gemmaをここで選択」の `clip_name` だけを切り替えます。MOSSは「MOSS画像生成用Qwen・このモデルは固定」から受け取るため、画像生成用Qwenまで変更されません。

- Gemma4：`gemma4_e4b_it_int8_convrot.safetensors`
- 既存Qwen：`qwen3.5_9b_int8_convrot.safetensors`

Gemma4は [Comfy-Org/gemma-4](https://huggingface.co/Comfy-Org/gemma-4/tree/main/text_encoders) のComfyUI対応E4B instructモデルを使用します。配布名を変えず `models/text_encoders` へ置きます。Ollamaの `gemma4:e4b` と同じE4B系列ですが、保存形式と量子化が異なるため、同一出力を保証しません。Ollamaへの接続や設定の読取は行いません。

`type` は付属例では `moss_image` のままです。今回のComfyUIは重みからGemma4を自動判別する分岐を持ち、Qwenへ選択を戻した時にも従来のMOSS用エンコーダーとして読み込める条件にそろえています。

既存のQwen共用ワークフロー3種類も残しています。こちらは台本とMOSSが従来どおり同じ読込ノードを参照します。Gemma版ではモデルが1種類増えるため、GemmaからMOSS用Qwenへの読み込み・退避のコストが加わり得ます。両読込ノードを同じQwen・同じ設定にした場合、ComfyUIの入力シグネチャによる出力キャッシュを再利用できる構成ですが、全キャッシュモードでの動作や時間差は保証しません。

## システムプロンプト

「① 作りたい動画をここに1つ入力」の `system_prompt` を編集します。初期値は従来の演出方針です。人物、場面、カメラ、文体などの方針を変えられます。

ノードは編集内容の後ろへ、4カットのJSON構造を指定する固定の指示を付けます。これはMOSSとH3の共通台本を読むために必要な形式です。システムプロンプトを省略した過去のAPIワークフローでは、従来と同じ全文を使用します。

同じ設定で比較する場合は、seedの「生成後の制御」を固定してください。物語を書く欄は引き続き `request` 1つです。

## 検証範囲

単体テストでは、指定CLIPと編集したシステムプロンプトが `TextGenerate` に渡ること、JSON形式指定が残ること、旧APIの省略時に従来の指示が維持されること、GemmaとMOSSの配線が独立していることを確認しています。実機結果は検証後に追記します。
