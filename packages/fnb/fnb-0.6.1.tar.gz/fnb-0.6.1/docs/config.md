# 設定ファイル

rfbは[TOML](https://toml.io)形式の設定ファイルを使用します。主な設定ファイルは`config.toml`または`rfb.toml`です。

## 設定ファイルの優先順位

設定ファイルは以下の順序で検索されます（優先度の高い順）：

1. `./rfb.toml` - プロジェクトローカル設定
2. `~/.config/rfb/config.toml` - グローバルユーザー設定（XDG準拠）
3. `C:\Users\ユーザー名\AppData\Local\rfb\config.toml` - Windowsユーザー設定
4. `./config/*.toml` - 設定の分割・統合用（開発/運用向け）

## 基本構造

設定ファイルは`fetch`セクションと`backup`セクションの2つの主要部分で構成されています：

```toml
[fetch.ラベル名]
# リモートからローカルへの取得設定

[backup.ラベル名]
# ローカルから外部ストレージへのバックアップ設定
```

## 設定フィールド

各セクションには以下のフィールドがあります：

| フィールド | 説明 | 例 |
|---|---|---|
| `label` | タスクの一意の識別子 | `"logs"` |
| `summary` | タスクの簡単な説明 | `"Fetch logs from server"` |
| `host` | リモートホスト名、またはローカル操作の場合は`"none"` | `"user@remote-host"` |
| `source` | rsyncのソースパス | `"~/path/to/source/"` |
| `target` | rsyncのターゲットパス | `"./local/backup/path/"` |
| `options` | rsyncオプションの配列 | `["-auvz", "--delete"]` |
| `enabled` | タスクが有効かどうか | `true` または `false` |

## 完全な設定例

```toml
# サーバーログのバックアップ設定

[fetch.logs]
label = "logs"
summary = "サーバーのログファイルを取得"
host = "user@production-server"
source = "/var/log/nginx/"
target = "./backup/logs/"
options = ["-auvz", "--delete", '--rsync-path="~/.local/bin/rsync"']
enabled = true

[backup.logs]
label = "logs"
summary = "ログファイルをNASにバックアップ"
host = "none"  # ローカル操作
source = "./backup/logs/"
target = "/Volumes/NAS/backups/logs/"
options = ["-auvz", "--delete"]
enabled = true

# データベースバックアップ設定

[fetch.database]
label = "database"
summary = "データベースバックアップを取得"
host = "user@db-server"
source = "/backup/daily/"
target = "./backup/database/"
options = ["-auvz", "--delete"]
enabled = true

[backup.database]
label = "database"
summary = "データベースバックアップをクラウドに保存"
host = "none"
source = "./backup/database/"
target = "/Users/username/OneDrive/Backups/database/"
options = ["-auvz", "--delete"]
enabled = true
```

## rsyncオプション

一般的に使用されるrsyncオプション：

- `-a` - アーカイブモード（再帰的、保持属性）
- `-u` - 更新されたファイルのみ転送
- `-v` - 詳細出力
- `-z` - 転送中にファイルを圧縮
- `--delete` - 送信元に存在しないファイルを削除
- `--dry-run` - テスト実行（ファイル変更なし）

カスタムrsyncパスを指定する例：

```toml
options = ["-auvz", "--delete", '--rsync-path="~/.local/bin/rsync"']
```

## 環境変数の展開

設定ファイル内のパスは環境変数と`~`（ホームディレクトリ）を自動的に展開します：

```toml
source = "$HOME/backups/"
target = "~/external-drive/backups/"
```

## 認証設定

SSH認証のために`.env`ファイルを使用することができます：

```env
SSH_PASSWORD=your-password-here
```

!!! tip "SSH認証のベストプラクティス"
    本番環境では、パスワード認証よりもSSHキー認証を使用することを強く推奨します。
