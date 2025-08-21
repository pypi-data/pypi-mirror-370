# API リファレンス

このページではfnbの内部APIとクラス構造を説明します。
fnbを拡張したり、他のプロジェクトから利用したりする場合に参考にしてください。

## モジュール構造

```
fnb/
├── __init__.py      # パッケージ初期化
├── backuper.py      # バックアップ実行ロジック
├── cli.py           # CLIエントリーポイント
├── config.py        # 設定モデル
├── fetcher.py       # フェッチ実行ロジック
├── gear.py          # rsync実行ロジック
├── generator.py     # 設定ファイル生成
└── reader.py        # 設定ファイル読み込み
```

## fnb.config

::: fnb.config
    options:
        show_source: true
        show_signature: true
        show_docstring: true

### RsyncTaskConfig

```python
class RsyncTaskConfig(BaseModel):
    """A single rsync task configuration

    Attributes:
        label (str): Unique identifier for the task.
        summary (str): Short description of the task.
        host (str): Remote host (e.g., "user@host") or "none" for local.
        source (str): Source path of rsync.
        target (str): Target path of rsync.
        options (List[str]): List of rsync options.
        enabled (bool): Whether the task is enabled.
    """
```

#### メソッド

- `is_remote` (property): タスクがリモートホストを使用するかどうかを判定
- `rsync_source` (property): rsyncのソースパス（リモートの場合は`host:path`形式）
- `rsync_target` (property): rsyncのターゲットパス

### FnbConfig

```python
class FnbConfig(BaseModel):
    """Configuration loader for fnb (Fetch'n'Backup)

    This class loads and parsed configuration files for fetch/backup tasks,
    expands environment variables, and provides access to task configurations.
    """
```

#### メソッド

- `get_enabled_tasks(kind)`: 指定されたタイプの有効なタスクのリストを返す
- `get_task_by_label(kind, label)`: 指定されたタイプとラベルを持つタスクを返す

### 補助関数

```python
def load_config(path: Path) -> RfbConfig:
    """Load configuration from a TOML file"""
```

## reader.py

### ConfigReader

```python
class ConfigReader:
    """Configuration reader for finding and loading rfb config files"""
```

#### メソッド

- `__init__(config_path=None)`: 設定ファイルのパスを指定して初期化
- `_load_file(path)`: TOMLファイルを読み込んでRfbConfigに変換
- `_get_default_config_path()`: デフォルトの設定ファイルパスを検索
- `_expand_env_vars()`: 設定内の環境変数とユーザーホームを展開
- `print_status()`: 設定済みタスクの状態を表示

## gear.py

### rsync実行関数

```python
def run_rsync(
    source: str,
    target: str,
    options: List[str],
    ssh_password: str | None = None,
    timeout: int = 30,
):
    """Execute an rsync command with optional SSH password automation"""
```

```python
def _run_rsync_with_password(
    command: str, ssh_password: str, timeout: int = 30
) -> bool:
    """Run rsync command with SSH password automation using pexpect"""
```

## fetcher.py

### フェッチ実行関数

```python
def run(
    task: RsyncTaskConfig, dry_run: bool = False, ssh_password: Optional[str] = None
) -> bool:
    """Execute the fetch operation for a given task"""
```

## backuper.py

### バックアップ実行関数

```python
def run(task: RsyncTaskConfig, dry_run: bool = False):
    """Execute the backup operation for a given label defined in config.toml"""
```

## generator.py

### 設定ファイル生成関数

```python
def create_config_file(force: bool = False) -> bool:
    """Create a default rfb.toml file in the current directory."""
```

```python
def run(force: bool = False) -> None:
    """CLI entry point for config file generation."""
```

## cli.py

### CLIコマンド関数

```python
@app.command()
def fetch(label: str, dry_run: bool = True, config: str = "examples/config.toml"):
    """Fetch data from remote server."""
```

```python
@app.command()
def backup(label: str, dry_run: bool = True, config: str = "examples/config.toml"):
    """Backup data to cloud or another local target."""
```

```python
@app.command()
def sync(
    label: str,
    dry_run: bool = typer.Option(
        True, "--dry-run", "-n", help="Show what would be done without making changes"
    ),
    ssh_password: str = typer.Option(
        None, "--ssh-password", help="Password for SSH authentication"
    ),
    config: str = typer.Option(
        None, "--config", "-c", help="Path to config file (default: auto-detect)"
    ),
):
    """Fetch from remote and backup to target in one step."""
```

```python
@app.command()
def init(
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing file without confirmation"
    ),
):
    """Generate a default config file (rfb.toml) in the current directory."""
```

```python
@app.command()
def status(
    config: str = typer.Option(
        None, "--config", "-c", help="Path to config file (default: auto-detect)"
    ),
):
    """Show status of configured fetch/backup tasks."""
```

## カスタム拡張例

### バックアップタスク完了後の通知送信

```python
from rfb.backuper import run as run_backup
from rfb.config import RsyncTaskConfig
import smtplib
from email.message import EmailMessage

def run_backup_with_notification(task: RsyncTaskConfig, dry_run: bool = False,
                               email: str = None):
    """Run backup task and send email notification on completion"""
    try:
        result = run_backup(task, dry_run)

        if email and result:
            msg = EmailMessage()
            msg['Subject'] = f"Backup completed: {task.label}"
            msg['From'] = "backup@example.com"
            msg['To'] = email
            msg.set_content(f"Backup task {task.label} completed successfully.")

            with smtplib.SMTP('smtp.example.com') as server:
                server.send_message(msg)

        return result

    except Exception as e:
        if email:
            # Send error notification
            msg = EmailMessage()
            msg['Subject'] = f"Backup failed: {task.label}"
            msg['From'] = "backup@example.com"
            msg['To'] = email
            msg.set_content(f"Backup task {task.label} failed with error: {str(e)}")

            with smtplib.SMTP('smtp.example.com') as server:
                server.send_message(msg)

        raise
```

### カスタム設定フィールドの追加

```python
from typing import Optional, List
from pydantic import BaseModel, Field
from rfb.config import RsyncTaskConfig

class ExtendedTaskConfig(RsyncTaskConfig):
    """Extended task configuration with notification options"""
    notify_email: Optional[str] = Field(None, description="Email to notify on completion")
    notify_on_error: bool = Field(True, description="Whether to send notifications on error")
    retention_days: Optional[int] = Field(None, description="Number of days to keep backups")
```

### プログラムからの使用例

```python
from pathlib import Path
from rfb.reader import ConfigReader
from rfb.fetcher import run as run_fetch
from rfb.backuper import run as run_backup

# 設定読み込み
reader = ConfigReader(Path("./my-config.toml"))

# タスク取得
fetch_task = reader.config.get_task_by_label("fetch", "docs")
backup_task = reader.config.get_task_by_label("backup", "docs")

# フェッチ実行
if fetch_task and fetch_task.enabled:
    print(f"Fetching {fetch_task.label}...")
    run_fetch(fetch_task, dry_run=False)

# バックアップ実行
if backup_task and backup_task.enabled:
    print(f"Backing up {backup_task.label}...")
    run_backup(backup_task, dry_run=False)
```
