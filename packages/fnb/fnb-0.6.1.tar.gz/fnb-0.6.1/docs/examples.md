# 使用例

このページではrfbを使った一般的なバックアップシナリオの例を紹介します。

## Webサーバーのバックアップ

Webサーバーのドキュメントルートとログをバックアップする設定例です。

```toml
[fetch.webroot]
label = "webroot"
summary = "Webサーバーのドキュメントルートを取得"
host = "user@webserver"
source = "/var/www/html/"
target = "./backup/webroot/"
options = ["-auvz", "--delete", "--exclude=cache/", "--exclude=tmp/"]
enabled = true

[backup.webroot]
label = "webroot"
summary = "Webサーバーのドキュメントルートをクラウドにバックアップ"
host = "none"
source = "./backup/webroot/"
target = "~/OneDrive/Backups/webserver/htdocs/"
options = ["-auvz", "--delete"]
enabled = true

[fetch.weblogs]
label = "weblogs"
summary = "Webサーバーのログを取得"
host = "user@webserver"
source = "/var/log/apache2/"
target = "./backup/weblogs/"
options = ["-auvz", "--delete", "--include=*.log", "--include=**/", "--exclude=*"]
enabled = true

[backup.weblogs]
label = "weblogs"
summary = "Webサーバーのログをクラウドにバックアップ"
host = "none"
source = "./backup/weblogs/"
target = "~/OneDrive/Backups/webserver/logs/"
options = ["-auvz", "--delete"]
enabled = true
```

使用例：

```bash
# ドキュメントルートのみをバックアップ
rfb sync webroot

# ログのみをバックアップ
rfb sync weblogs

# 両方をバックアップ（2つのコマンドを実行）
rfb sync webroot && rfb sync weblogs
```

## データベースバックアップ

データベースダンプファイルをバックアップする設定例です。

```toml
[fetch.mysql]
label = "mysql"
summary = "MySQLのバックアップを取得"
host = "user@dbserver"
source = "/var/backups/mysql/"
target = "./backup/mysql/"
options = ["-auvz", "--delete"]
enabled = true

[backup.mysql]
label = "mysql"
summary = "MySQLのバックアップをクラウドにバックアップ"
host = "none"
source = "./backup/mysql/"
target = "~/OneDrive/Backups/database/mysql/"
options = ["-auvz", "--delete"]
enabled = true
```

使用例：

```bash
# 通常のバックアップ
rfb sync mysql

# ドライラン（変更なし）
rfb sync mysql --dry-run
```

## ホームディレクトリバックアップ

リモートサーバーのホームディレクトリをバックアップする設定例です。

```toml
[fetch.home]
label = "home"
summary = "ホームディレクトリを取得"
host = "user@server"
source = "~/"
target = "./backup/home/"
options = ["-auvz", "--delete", "--exclude=.cache/", "--exclude=node_modules/"]
enabled = true

[backup.home]
label = "home"
summary = "ホームディレクトリをNASにバックアップ"
host = "none"
source = "./backup/home/"
target = "/Volumes/NAS/backups/home/"
options = ["-auvz", "--delete"]
enabled = true
```

使用例：

```bash
# ホームディレクトリをフェッチのみ（バックアップなし）
rfb fetch home

# フェッチ後、バックアップを実行
rfb backup home

# 一括実行
rfb sync home
```

## 定期バックアップの自動化

cronを使って定期バックアップを設定する例です。

```bash
# crontabに追加：毎日午前2時にバックアップを実行
0 2 * * * cd /path/to/rfb && /usr/local/bin/rfb sync all > /tmp/rfb-log.txt 2>&1
```

または、systemdタイマーを使用する場合：

```ini
# /etc/systemd/system/rfb-backup.service
[Unit]
Description=Run rfb backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/rfb sync all
WorkingDirectory=/path/to/rfb

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/rfb-backup.timer
[Unit]
Description=Run rfb backup daily

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

有効化コマンド：

```bash
sudo systemctl enable rfb-backup.timer
sudo systemctl start rfb-backup.timer
```

## カスタムrsyncパスの使用

特定の環境（共有ホスティングなど）でカスタムrsyncパスを指定する例です。

```toml
[fetch.custom]
label = "custom"
summary = "カスタムrsyncパスを使用してデータを取得"
host = "user@shared-hosting"
source = "~/public_html/"
target = "./backup/site/"
options = ["-auvz", "--delete", '--rsync-path="~/bin/rsync"']
enabled = true
```

## 複数設定ファイルの使用

開発環境と本番環境で別々の設定ファイルを使用する例です：

```bash
# 開発環境用の設定
rfb sync dev-site --config dev-config.toml

# 本番環境用の設定
rfb sync prod-site --config prod-config.toml
```

## SSHパスワード認証の自動化

`.env`ファイルを使用したSSHパスワード認証の例です：

```env
# .env ファイル（gitignoreに追加すること）
SSH_PASSWORD=your-secure-password
```

使用例：

```bash
# .envファイルから自動的にパスワードを使用
rfb sync site
```

!!! warning "セキュリティ警告"
    本番環境ではパスワード認証よりもSSHキー認証を推奨します。
