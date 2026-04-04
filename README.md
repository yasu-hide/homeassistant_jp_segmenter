# Japanese Segmenter Assistant for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Country](https://img.shields.io/badge/Country-JP-blue.svg)

Home Assistant の音声アシスタント（Assist）において、日本語の「助詞」による意図解釈（Hassil）の失敗を、軽量な形態素解析によって解決するカスタムコンポーネントです。

## 解決する課題 (The Problem)

標準の Home Assistant Assist（Hassil）は、日本語のような不分かち書き言語のパースが苦手です。
例えば、**「B'zのLOVE PHANTOMを流して」** と発話した場合：

- **標準状態:** `artist_name` スロットに `"B'zのLOVE PHANTOM"` と丸ごと入ってしまい、検索に失敗する。
- **本コンポーネント導入後:** 内部で `"B'z の LOVE PHANTOM"` と分かち書きを行うため、Hassil が正確に `"B'z"` と `"LOVE PHANTOM"` を抽出できるようになります。

これにより、Gemini 等の LLM エージェントのクォータ（1日20回制限など）を消費することなく、ローカル環境のみで高いインテント的中率を実現します。

## 特徴 (Features)

- **超軽量:** `TinySegmenter` を採用し、辞書不要で低リソースな分かち書きを実現。
- **低遅延:** ローカルで完結するため、音声操作のレスポンスを損ないません。
- **疎結合:** 既存の会話パイプラインに「前処理フィルター」として割り込むため、システムの安定性を維持します。

## インストール方法 (Installation)

### 1. HACS にカスタムリポジトリとして追加
本リポジトリは現在 HACS のデフォルトリストには含まれていないため、手動で追加する必要があります。

1. Home Assistant のサイドバーから **HACS** を選択。
2. 右上の **︙ (三点リーダー)** > **Custom repositories** をクリック。
3. **Repository** に本リポジトリの URL を入力。
4. **Category** で `Integration` を選択し、**Add** をクリック。
5. リストに表示された `Japanese Segmenter Assistant` をダウンロード（Download）してください。

### 2. Home Assistant の再起動
インストール完了後、Home Assistant を再起動してください。

### 3. 統合のセットアップ
1. **設定 > デバイスとサービス > 統合を追加** をクリック。
2. `Japanese Segmenter Assistant` を検索して追加します。

## 設定 (Configuration)

1. **設定 > 音声アシスタント** を開きます。
2. 使用しているアシスタントの設定画面に入ります。
3. **会話エージェント** の項目で、`Japanese Segmenter Assistant` を選択して保存します。

## 技術仕様 (Technical Details)

- **Backend:** Python (Home Assistant Custom Component)
- **Tokenizer:** [TinySegmenter](http://chasen.org/~taku/software/TinySegmenter/)
- **License:** MIT

## 開発者向け (SRE Note)
本プロジェクトは、LLM への依存度を下げ、エッジコンピューティングによる「100%ローカルなスマートホーム」の信頼性（Reliability）向上を目的に開発されました。
