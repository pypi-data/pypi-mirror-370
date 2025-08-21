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

### From PyPI (Recommended)

```bash
# Install from PyPI
pip install fnb

# Or using uv
uv add fnb
```

### From Source

- Python 3.12 or higher is required.
- Setup the project using `uv`

```bash
git clone https://gitlab.com/qumasan/fnb.git
cd fnb
uv venv
uv pip install -e .
```

---

## 🧰 コマンド例

```bash
# Initialize configuration files (fnb.toml and .env files)
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

### Version Management

This project uses automated semantic versioning with GitLab releases:

```bash
# Preview version bump
task version

# Execute version bump and changelog update
task version:bump

# Create GitLab release
task release

# Complete release workflow (test → format → bump → release)
task release:full
```

**Current Version**: v0.8.0 - [View Release](https://gitlab.com/qumasan/fnb/-/releases/0.8.0)

### CI/CD Pipeline

GitLab CI/CD pipeline provides automated testing, building, and deployment:

**Stages:**
- `test`: Unit tests, code quality, integration tests (separate job)
- `build`: Package building with `uv build`
- `deploy-test`: TestPyPI deployment (manual, tags only)
- `deploy-prod`: PyPI deployment (manual, tags only)

**Required CI Variables for Deployment:**
```bash
# GitLab Settings → CI/CD → Variables
TESTPYPI_API_TOKEN  # TestPyPI API token for testing releases
PYPI_API_TOKEN      # PyPI API token for production releases
```

**Local CI Simulation:**
```bash
# Run tests as they run in CI (unit tests only)
task test:ci

# Run unit tests only (fast feedback)
task test:unit

# Run integration tests only
task test:integration

# Run all tests
task test
```

### Test Structure

Tests are organized into two directories for optimal development workflow:

- **tests/unit/**: 9 files, 124 tests - Fast unit tests (1.65s)
- **tests/integration/**: 1 file, 23 tests - Comprehensive workflow tests (3.25s)

Both directory-based and marker-based execution are supported:
```bash
# Directory-based (recommended)
task test:unit          # tests/unit/ only
task test:integration   # tests/integration/ only

# Marker-based (backward compatibility)
pytest -m "not integration"  # unit tests
pytest -m "integration"      # integration tests
```

### Test Coverage

Current test coverage is **87%** (exceeds 83% target) with comprehensive error handling and integration testing:

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

- 🛠️ Development, Issues, Merge Requests: [GitLab](https://gitlab.com/qumasan/fnb)
- 🌏 Public Mirror and Discussions: GitHub
- 📦 PyPI Package: [fnb](https://pypi.org/project/fnb/) (v0.8.0)
- 📖 Documentation: [GitLab Pages](https://qumasan.gitlab.io/fnb/)

Please use **GitLab** for development contributions, bug reports, and feature requests.
For documentation viewing and community discussions, feel free to visit the GitHub mirror.

### Development Workflow

See [CLAUDE.md](./CLAUDE.md) for detailed development guidelines including:
- Testing and coverage requirements (83%+)
- Version management and release workflow
- GitLab integration best practices
