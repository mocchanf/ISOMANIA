# 🎬 ISOmania - MP4をDVD ISOに変換するアプリ

MP4動画をドラッグ＆ドロップで、DVD用のISOファイルに変換できるmacOSアプリです。  
ブラウザベースのStreamlitアプリを `.app` 化しており、インストール不要で手軽に使えます。

---

## 🛠️ 使い方（macOS）

1. [Releasesページ](https://github.com/your-username/ISOmania/releases) から `ISOmania.dmg` をダウンロード
2. `ISOmania.app` を開きます（初回は右クリック →「開く」で実行許可が必要な場合があります）
3. ブラウザが起動し、変換アプリが表示されます
4. MP4ファイルを選んで「変換する！」をクリック
5. 変換完了後、ISOファイルをダウンロードできます

---

## 💻 動作環境

- macOS 12（Monterey）以上 推奨
- `ffmpeg`, `dvdauthor`, `mkisofs` がインストールされている必要があります

インストール例（Homebrew）:

```bash
brew install ffmpeg dvdauthor cdrtools
