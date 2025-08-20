# fnb — Fetch'n'Backup

**fnb** は、2段階のシンプルなバックアップツールです。
rsync をベースに、リモートからのデータ取得とローカル/クラウドへのバックアップを手軽に実行できます。

> Simple config. Sharp execution. Safe data.

## 🚀 主な機能

1. **Fetch** — リモートサーバーからローカルにデータを取得
2. **Backup** — ローカルデータをOneDrive等にバックアップ
3. **Sync** — Fetch + Backup を一括実行
4. **Status** — 最新スナップショットの状態を表示
5. **Init** — 初期設定ファイル（`config.toml`）を生成

## 🔰 Quick Start

```bash
# 設定ファイルを作成
fnb init

# 設定ファイルを編集
vi fnb.toml
vi .env.plain
cp .env.plain .env

# コマンドを実行
fnb sync logs
```

`fnb init`で必要な設定ファイルのひな型を生成できます。
`fnb.toml`を編集してパスを設定します。
`.env.plain`を編集してリモートサーバーのログインパスワードを設定します。

> `.env.plain`の内容は平文で保存されることに注意してください。
> このファイルを`.env`というファイル名に変更して、`dotenvx`で暗号することを推奨します。

### 🔐 環境変数の暗号化（推奨）

```bash
# 環境変数を暗号化
dotenvx encrypt -f .env
# .env: 暗号化されたパスサード
# .env.keys: 秘密鍵

# rfbコマンドを実行
dotenvx run -- fnb sync logs
```

`dotenvx`で`.env`を暗号化できます。

## 🧰 コマンド例

```bash
# Fetch（リモート → ローカル）
fnb fetch TARGET_LABEL

# Backup（ローカル → クラウドストレージなど）
fnb backup TARGET_LABEL

# Fetch → Backup を順番に一括実行
fnb sync TARGET_LABEL

# 設定内容の確認
fnb status

# config.toml の初期化
fnb init
```

## 🛠️ インストール

```bash
# uv を使用してプロジェクトセットアップ
uv venv
uv pip install -e .
```

詳細は[インストールガイド](installation.md)を参照してください。

## 📦 CLIコマンド一覧

`fnb` コマンドは以下のようなサブコマンドで構成されます：

- `fetch`: リモートからデータを取得
- `backup`: ローカルデータをバックアップ
- `sync`: fetch + backup を連続実行
- `status`: 有効なタスクの状態を確認
- `init`: 初期設定ファイル（`rfb.toml`, `.env`）を生成

## 📝 設定ファイル

**config.toml**

各処理対象のディレクトリごとに
`fetch` / `backup`
の設定を持ちます。

```toml
[fetch.SECTION_NAME]
label = "TARGET_LABEL"
summary = "Fetch data from remote server"
host = "user@remote-host"
source = "~/path/to/source/"
target = "./local/backup/path/"
options = ["-auvz", "--delete", '--rsync-path="~/.local/bin/rsync"']
enabled = true

[backup.SECTION_NAME]
label = "TARGET_LABEL"
summary = "Backup data to cloud storage"
host = "none"    # <- ローカル操作
source = "./local/backup/path/"  # <- fetchのtargetパス
target = "./cloud/backup/path/"
options = ["-auvz", "--delete"]
enabled = true
```

詳細な設定例は[設定ファイルガイド](usage/configuration.md)を参照してください。

## 🔐 認証について

SSH パスワード入力は `pexpect` を用いて自動化されます。
必要に応じて `.env` ファイルに接続設定等を記載可能です。

## 🪪 ライセンス

MITライセンス

## 📬 貢献

Issue や PR は歓迎です。
お気軽にどうぞ。ドキュメントの改善提案も歓迎です。
