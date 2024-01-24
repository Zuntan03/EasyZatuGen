# EasyZatuGen

概要は[こちら](https://twitter.com/Zuntan03/status/1744195658029117523)。

日本語の短いテーマから、画像生成プロンプト＆和訳とアップスケールした絵とセリフと感情付き音声を、雑然と生成する EasyZatuGen です。

[AutoAWQ](https://github.com/casper-hansen/AutoAWQ)&[calm2](https://huggingface.co/cyberagent/calm2-7b-chat)-[AWQ](https://huggingface.co/TheBloke/calm2-7B-chat-AWQ) と [StreamDiffusion](https://github.com/cumulo-autumn/StreamDiffusion/) と [Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2) の三点盛りで、すべてをローカルで生成します。

## インストール

Geforce RTX 3060 **VRAM 12GB** 以上を搭載した Widows PC で簡単に動作します。  
画像生成なしでセリフの生成と読み上げのみなら **VRAM 8GB** で動作します（`[画像生成]-[画像を生成する]` を無効）。  
未成年の方は利用しないでください。

1. [Install-EasyZatuGen.bat](https://github.com/Zuntan03/EasyZatuGen/raw/main/EasyZatuGen/setup/Install-EasyZatuGen.bat) を右クリックから保存して、インストール先のフォルダで実行します。  
 **インストール先のフォルダは、スペースを含まない英数字のみの浅いパス (`C:\EasyZatuGen\` など) にしてください。**
	- **`WindowsによってPCが保護されました` と表示されたら、`詳細表示` から `実行` します。**
	- ファイルの配布元を `Ctrl+Click` で確認して、問題がなければ `y` を入力してください。
	- Pythonへのネットワーク許可は、`キャンセル` してしまっても正常に動作するようです。
2. 15分程度（ネット回線によります）のインストールが終わると、`EasyZatuGen` のウィンドウが立ち上がります。
	- 初回起動時は様々なモデルを初期化するため、ウィンドウが表示されてから実際に動き出すまでに 1分程度の時間が掛かります。
	- ウィンドウ上部の入力欄に日本語でテーマを入力すると、`output/` フォルダに PNG 画像や WAV 音声を生成します。

### インストールのトラブル対策

- アバストなどのウィルスチェックソフトが有効だと、インストールに失敗する場合があります。
- Windows PC の管理者権限がないと、インストールに失敗する場合があります。
- プロキシ環境などでインストールに失敗する場合は、Python 3.10 系にパスを通して `EasyZatuGen/setup/Setup-Venv.bat` のコメントを解除してから `EasyZatuGen/setup/Setup-EasyZatuGen.bat` で成功する場合があります。

## 使いかた

`EasyZatuGen.bat` をダブルクリックすると、`EasyZatuGen` と `Style-Bert-VITS2 読み上げサーバー` が立ち上がります。  
`Update.bat` で `EasyZatuGen` を更新できます。

### テーマの書きかた　！重要！ここだけは読んで！

`日本語でのテーマ入力と｛メインキャラクター｝の指定｜追加の画像生成プロンプト`

例）`バレンタインデーの学校で女学生の｛ひまりちゃん｝がさゆり先輩にチョコレートを渡しながら告白。|(2girls, holding gift box: 1.4)`

- 日本語でテーマを入力し、パイプ (`｜`, `|`) 以降で画像生成の追加プロンプトを指定します。
- **テーマ内の中カッコ (`｛｝`, `{}` ) で、メインキャラクターを指定します。**
	- **メインキャラクターを指定することで、キャラクターが適切に話すようになります。**  
- `[サンプル]` メニューから他の例を確認できます。

#### テーマの書きかた TIPS

- テーマでの末尾に `（キャラ名）「」` を追記することで、セリフを誘導することもできます。  
	例）`バレンタインデーの学校で女学生の｛ひまりちゃん｝がさゆり先輩にチョコレートを渡しながら告白。さゆり先輩「ひまりちゃん、あらたまってなぁに？」`
- 追加の画像生成プロンプトには、画像で外したくない要素を入力します。
	- 外したくない要素は、LoRA で担保することもできます。

### 重要 TIPS

#### 重くてテーマの入力がカクつく

- `[ツール]-[クリップボード連携]` で、お好みのエディタでテーマや追加プロンプトを記述してコピーで連携します。
	- **お好みのエディタでコピーするテキストに、パイプ (`｜`, `|`) を含める必要があります。**  
	パイプを末尾につけるとテーマのみの更新、先頭につけると追加プロンプトのみの更新ができます。

#### 人の作ったテーマを使ったり、自分の作ったテーマをシェアしたい

- 生成された PNG 画像のメタ情報に、EazyZatuGen の設定が入っていますので、画像で受け渡しができます。
	- **PNG 画像を EazyZatuGen にドラッグ＆ドロップすると画像保存時の設定を適用できます。**
	- Twitter などの多くのサービスでは PNG 画像のメタ情報が自動的に削除されます。
		- [Catbox](https://catbox.moe/) でシェアするとメタ情報が残ります。
		- `[ファイル]-[JSON エクスポート]` で保存した JSON ファイルでも、同様に設定を共有できます。
- `[読み上げ]` でのボイス指定や、利用している `モデル` や `LoRA` の配布元もシェアされます。
	- **`モデル` や `LoRA` を開いた場所に `*.civitai.info` ファイルがあれば、トリガーワードや配布元の情報を取り込みます。**

## FAQ よくある質問と回答

### `モデル` FAQ

#### きれいな画像が生成されない

- EazyZatuGen は [LCM](https://huggingface.co/latent-consistency/lcm-lora-sdv1-5) を使用しているため、モデルとの相性があります。
	- 相性の悪くないモデルを `[モデル]-[モデルをダウンロードする]` からダウンロードできます。
	- おすすめのモデルがありましたら、ぜひシェアしてください。

### `読み上げ` FAQ

#### 読み上げのやり取りが進まない

- `[読み上げ]-[セリフ生成の最大トークン数]` を引き上げると、より長いやり取りが生成されます。
	- 生成したやり取りの再生を、途中で止める機能はまだありません。

#### NSFW な読み上げをしたい

- `[読み上げ]-[キャラの声]` を `-nsfw` にして、`スタイル` を `Neutral` 以外に設定し、`スタイルの強さ` を `15～25` あたりにします。
	- 文面や `キャラの声` や `スタイル` によって、`スタイルの強さ` を調整してください。

## 参照

- [casper-hansen/AutoAWQ](https://github.com/casper-hansen/AutoAWQ/)
- [cyberagent/calm2-7b-chat](https://huggingface.co/cyberagent/calm2-7b-chat/)
- [TheBloke/calm2-7B-chat-AWQ](https://huggingface.co/TheBloke/calm2-7B-chat-AWQ/)
- [cumulo-autumn/StreamDiffusion](https://github.com/cumulo-autumn/StreamDiffusion/)
- [litagin02/Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2/)
- [litagin/style_bert_vits2_jvnv](https://huggingface.co/litagin/style_bert_vits2_jvnv/)
<!-- - [litagin/style_bert_vits2_okiba](https://huggingface.co/litagin/style_bert_vits2_okiba/)
- [litagin/style_bert_vits2_nsfw](https://huggingface.co/litagin/style_bert_vits2_nsfw/) -->

## ライセンス

以下を除き、このリポジトリの内容は [MIT License](./LICENSE.txt) です。

- `EasyZatuGen/setup/tkinter-PythonSoftwareFoundationLicense.zip` は Python Software Foundation License です。
