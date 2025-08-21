# 基本コマンド

rfbには以下の主要コマンドがあります。

## init

最初にこのコマンドを使って、`rfb`の設定ファイル（`rfb.toml`や`.env`）を作成します。

```bash
rfb init [--force]
```

カレントディレクトリに初期設定ファイル `rfb.toml` を生成します。

**オプション**：

- `--force`, `-f` - 既存の設定ファイルを上書きします

**使用例**：

```bash
# 基本的な使用法
rfb init

# 既存のファイルを上書き
rfb init --force
```

## status

現在設定されている`fetch`や`backup`タスクの一覧とディレクトリの状態を確認できます。

```bash
rfb status [--config CONFIG_PATH]
```

設定済みのfetch/backupタスクの状態を表示します。

**オプション**：

- `--config`, `-c` - 設定ファイルのパスを指定します（デフォルト：自動検出）

**使用例**：

```bash
# デフォルト設定ファイルを使用
rfb status

# 特定の設定ファイルを指定
rfb status --config ./my-config.toml
```

## fetch

リモートサーバー上のファイルを、設定にしたがって自分のパソコンにコピーするコマンドです。

```bash
rfb fetch LABEL [--dry-run] [--config CONFIG_PATH]
```

リモートサーバーからデータを取得します。

**引数**：

- `LABEL` - 設定ファイルで定義されたタスクラベル

**オプション**：

- `--dry-run` - 実際のファイル転送を行わずに実行内容をプレビュー
- `--config`, `-c` - 設定ファイルのパスを指定（デフォルト：自動検出）

**使用例**：

```bash
# 基本的な使用法
rfb fetch logs

# ドライラン（変更なし）
rfb fetch logs --dry-run
```

## backup

パソコン上のファイルを、外部ストレージなどにバックアップします。

```bash
rfb backup LABEL [--dry-run] [--config CONFIG_PATH]
```

ローカルデータをクラウドやNASなどの外部ストレージにバックアップします。

**引数**：

- `LABEL` - 設定ファイルで定義されたタスクラベル

**オプション**：

- `--dry-run` - 実際のファイル転送を行わずに実行内容をプレビュー
- `--config`, `-c` - 設定ファイルのパスを指定（デフォルト：自動検出）

**使用例**：

```bash
# 基本的な使用法
rfb backup logs

# ドライラン（変更なし）
rfb backup logs --dry-run
```

## sync

`fetch`（取得）と`backup`（保存）を連続して実行する、便利な一括コマンドです。


```bash
rfb sync LABEL [--dry-run] [--ssh-password PASSWORD] [--config CONFIG_PATH]
```

fetchとbackupを連続して実行します。

**引数**：

- `LABEL` - 設定ファイルで定義されたタスクラベル

**オプション**：

- `--dry-run`, `-n` - 実際のファイル転送を行わずに実行内容をプレビュー
- `--ssh-password` - SSH認証用のパスワード
- `--config`, `-c` - 設定ファイルのパスを指定（デフォルト：自動検出）

**使用例**：

```bash
# 基本的な使用法
rfb sync logs

# ドライラン（変更なし）
rfb sync logs --dry-run

# SSHパスワードを指定
rfb sync logs --ssh-password "your-password"
```

!!! warning "セキュリティ注意"
    コマンドラインでSSHパスワードを直接指定するのはセキュリティリスクがあります。
    代わりに`.env`ファイルの使用や、SSHキー認証を検討してください。
