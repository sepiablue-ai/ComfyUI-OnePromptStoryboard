# 独立環境での導入・生成検証

2026年10月26日、master環境とは別フォルダーに公式ComfyUIと新規専用venvを作り、このrepoをGitHubからクローンして検証しました。masterのsite-packagesを参照しない環境です。モデルと外部ノード2つはmasterからリンクしています。

## 結果

| ワークフロー | 所要時間 | 結果 |
| --- | --- | --- |
| `all_in_one_magic_battle.api.json` | 207.51秒 | 文章1つ→共通台本→MOSS→参照画像1枚→H3動画保存 |
| `h3_from_saved_storyboard.api.json` | 170.29秒 | 上記の画像を固定し、H3のカメラ指示4か所だけ変更して動画保存 |

どちらも1024×1792、24fps、345フレーム、14.375秒、AAC音声です。映像345フレームと音声450フレームを全てデコードできました。生成中はWebSocketの完了・エラー通知を待ち、生成状態や履歴をポーリングしていません。履歴は通知後に取得しました。

H3のみの例では `303.inputs.text` を変更し、各カットのカメラを固定カメラへ指定し直しました。画像の読み込み先は例の `storyboard.png` のまま、実際のストーリーボードを無加工コピーして配置しました。元と入力画像のSHA-256は両方 `697a7667ce874be41fbaa0a2f7427db73e29cfb2d4cc5e457827c441e7251967` です。実行履歴のグラフにMOSS生成や台本生成ノードがないことも確認しています。

画風LoRAは使用していません。MOSSの枠線補修も無効です。動画では4つの場面への移行と、プロンプト変更による構図の違いが見られました。ただし発光で顔が隠れる場面があり、固定カメラ等の指示への完全な追従を保証する検証ではありません。品質確認用には実出力から無加工で静止フレームを取り出しました。

## 公開コードとの照合

| 依存 | 公開repo | 検証コミット | masterとの照合 |
| --- | --- | --- | --- |
| ComfyUI本体 | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | `355cd6b14c92c19ac3188fe528e47a3f21ef5178` | 公式コミット、masterに追跡対象の変更なし |
| MOSS Storyboard | [ZenHG/ComfyUI-MOSS-Storyboard](https://github.com/ZenHG/ComfyUI-MOSS-Storyboard) | `4d848d5854c7e39ef8cbb8b8163fec7d31963dd6` | 公開60ファイル全てハッシュ一致 |
| FastH3高速化 | [sepiablue-ai/ComfyUI-FastH3-OmniRef-Accel](https://github.com/sepiablue-ai/ComfyUI-FastH3-OmniRef-Accel) | `c3e8e84b36124d5adbf801c5d2e7e42665fe60a8` | 公開25ファイル全てハッシュ一致 |
| 本repo | ComfyUI-OnePromptStoryboard | `ab044e6cb38de72b457b476aebb5c0617cc367d7` | GitHubからクローン |

MOSSの検証版は0.1.2です。取得時の公開最新版とは異なるので、再現時は上記コミットに合わせてください。最新版との互換性は未確認です。

外部ノード2つについて、公開repoにない追加のPython・JavaScript・DLL等の実行コードは検出されませんでした。FastH3は本repoと同じ作者の公開ノードで、他作者のノードではありません。LBH実装はFastH3 repoの `vendor/lbh_3d.py` に同梱されており、PC内の別のLBHノードは不要です。それ以外のワークフローノードはComfyUI本体または本repoの実装です。

## 環境

- Windows、RTX 4070 12GB、GPU0
- ComfyUI 0.42.0、Python 3.13.13、新規venvの `include-system-site-packages=false`
- PyTorch 2.14.0+cu130、torchvision 0.29.0+cu130
- comfy-kitchen 0.2.39、comfy-aimdo 0.5.6、triton-windows 3.8.0.post28
- PyAV 18.1.0、フロントエンド1.55.18
- PyPIとPyTorch公式CUDA 13.0のインデックスから、ComfyUIのrequirementsと追加の `triton-windows`・検証クライアント用 `websocket-client` を専用venvへ導入
- 起動時は `CUDA_VISIBLE_DEVICES=0`、`PYTHONIOENCODING=utf-8`、`--disable-pinned-memory`

モデル10件の選択肢と必要ノードの登録を確認し、単体・接続テスト10件も成功しています。これはAPI形式での実行検証です。画面からの読み込みと操作は未検証です。モデルダウンロード自体は、既存モデルをリンクしたため今回の検証範囲に含みません。
