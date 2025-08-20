# fnb — Fetch'n'Backup

**fnb** is a simple two-step backup tool, powered by `rsync`.
It gives you two handy commands:
`fetch` (to pull from remote), and
`backup` (to save to somewhere safe).

Under the hood? Just good old `rsync` — no magic, just sharp automation.

- Simple config. Sharp execution. Safe data.
- Use them one by one, or `sync` them all in one go.

---

## 🚀 Features

1. **Fetch** — Retrieve data from a remote server to your local machine
2. **Backup** — Save local data to external storage
3. **Sync** — Run Fetch and Backup together in one go
4. **Init** — Generate an initial config file (`fnb.toml`)

---

## ⚙️ Installation and Setup

- Python 3.12 or higher is required.
- Setup the project using `uv`

```bash
uv venv
uv pip install -e .
```

---

## 🧰 コマンド例

```bash
# Initialize configuration files (rfb.toml and .env files)
fnb init

# Check the current config
fnb status

# Fetch: remote -> local
fnb fetch TARGET_LABEL

# Backup: local -> external
fnb backup TARGET_LABEL

# Run Fetch → Backup in one go
fnb sync TARGET_LABEL
```

---

## 🔧 設定ファイル

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

### 設定ファイルの優先順位（高 → 低）

1. `./fnb.toml`                   ← プロジェクトローカル設定
2. `~/.config/fnb/config.toml`    ← グローバルユーザー設定（XDG準拠）
3. `C:\Users\ユーザー名\AppData\Local\fnb\config.toml`    ← グローバルユーザー設定（Windowsの場合）
4. `./config/*.toml`              ← 設定の分割・統合用（開発/運用向け）

---

## 🔐 Authentication

SSH password input can be automated using `pexpect`.
You can also define connection settings in a `.env` file if needed.
Run `fnb init env` to create the initial `.env` file.

---

## 🧪 Development

- `Python3` - version 3.12 or higher
- `uv` - package management
- `Typer` - CLI framework
- `Pydantic` - config modeling
- `pexpect` - SSH automation
- `python-dotenv` - environment variable support
- `pytest` - testing framework (83% coverage)
- `mkdocs-material` - documentation
- `pre-commit` - run checks before each commit
- `ruff` - fast Python linter and formatter
- `commitizen` - conventional commit tagging and changelog automation

### Test Coverage

Current test coverage is **83%** with comprehensive error handling and integration testing:

- **backuper.py**: 83% - Backup operation failure scenarios
- **fetcher.py**: 85% - SSH authentication and fetch failures
- **cli.py**: 99% - CLI command error scenarios
- **reader.py**: 89% - Configuration reading and validation
- **gear.py**: 87% - SSH automation with pexpect
- **env.py**: 68% - Environment variable handling

### Integration Testing

Complete integration test suite with **23 tests (100% success rate)**:

- **CLI Workflow Integration**: 7 tests covering init → status → fetch/backup/sync workflows
- **Multi-Module Integration**: 6 tests verifying config → reader → gear → operation flows
- **Sync Workflow Integration**: 6 tests for complete fetch-then-backup sequences
- **End-to-End Integration**: 2 tests simulating realistic user workflows
- **Test Infrastructure**: Strategic mocking, external dependency isolation, reliable deterministic testing

## 🪪 License

MIT

## 🛠️ Contributing

This project is maintained in two repositories:

- 🛠️ Development, Issues, Merge Requests: GitLab
- 🌏 Public Mirror and Discussions: GitHub

Please use **GitLab** for development contributions, bug reports, and feature requests.
For documentation viewing and community discussions, feel free to visit the GitHub mirror.
