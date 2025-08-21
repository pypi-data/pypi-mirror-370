# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fnb (Fetch'n'Backup) is a Python-based CLI tool (version 0.8.0) that provides a two-step backup workflow using `rsync`. The tool allows users to:
1. **Fetch** data from remote servers to local storage
2. **Backup** local data to external/cloud storage
3. **Sync** both operations in sequence

The application is built with Typer for CLI, Pydantic for configuration validation, and uses `rsync` with `pexpect` for SSH automation. It requires Python 3.12+.

## Development Commands

### Core Development Tasks (use `task` command)
- `task test` - Run all tests with coverage (147 tests, 87% coverage)
- `task test:unit` - Run unit tests only (124 tests, 83% coverage, 1.65s)
- `task test:integration` - Run integration tests only (23 tests, 68% coverage, 3.25s)
- `task test:ci` - Simulate complete CI pipeline locally (unit tests → format → pre-commit)
- `task lint` - Format code with ruff
- `task lint:pre-commit` - Run all pre-commit hooks
- `task docs` - Serve documentation locally
- `task docs:build` - Build documentation as static HTML

### Version Management Tasks
- `task version` - Preview version bump and changelog changes
- `task version:bump` - Execute version bump with changelog update
- `task release` - Create GitLab release for current version tag
- `task release:full` - Complete release workflow (test → format → bump → release)

### Package Management (using `uv`)
- `uv venv` - Create virtual environment
- `uv pip install -e .` - Install in development mode
- `uv run fnb --help` - Run CLI from source
- `uv run pytest` - Run tests directly
- `uv run ruff format src tests` - Format code directly
- `uv pip list --outdated` - Show outdated packages

### Testing
- Run single test: `uv run pytest tests/unit/test_specific.py::test_function`
- Run with coverage: `uv run pytest --cov=fnb --cov-report=term`
- Test configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`
- **Test Structure**: 
  - `tests/unit/`: 9 files, 124 unit tests (fast execution: 1.65s)
  - `tests/integration/`: 1 file, 23 integration tests (comprehensive: 3.25s)

## Architecture Overview

### Core Modules
- **`cli.py`** - Typer-based CLI entry point with commands: `init`, `status`, `fetch`, `backup`, `sync`, `version`
- **`config.py`** - Configuration loading/validation using Pydantic (`FnbConfig`, `RsyncTaskConfig`)
- **`reader.py`** - Config file discovery and status reporting (`ConfigReader`)
- **`gear.py`** - Core `rsync` execution with SSH password automation via `pexpect`
- **`fetcher.py`/`backuper.py`** - Command implementations that delegate to `gear.py`
- **`generator.py`** - Config file generation for `fnb init`
- **`env.py`** - Environment variable handling with `python-dotenv`

### Configuration System
- Uses TOML format with sections `[fetch.SECTION_NAME]` and `[backup.SECTION_NAME]`
- Configuration discovery order: `./fnb.toml` → `~/.config/fnb/config.toml` → platform-specific paths
- Each task requires: `label`, `summary`, `host`, `source`, `target`, `options`, `enabled`
- Remote tasks use SSH with optional password automation via `.env` file

### Data Flow
1. CLI command (`fetch`/`backup`/`sync`) receives label parameter
2. `ConfigReader` loads and validates TOML configuration
3. Task lookup by label in appropriate section (`fetch.*` or `backup.*`)
4. Task execution via `gear.run_rsync()` with optional SSH automation
5. Error handling and user feedback through Typer

## Key Configuration Files
- **`pyproject.toml`** - Project metadata, dependencies, tool configuration (ruff, pytest, commitizen, hatchling build system)
- **`Taskfile.yml`** - Development task automation using Task runner
- **`fnb.toml`** - Runtime configuration (created by `fnb init`)
- **`.env`** - Environment variables for SSH passwords (optional)
- **`mkdocs.yml`** - Documentation site configuration
- **`uv.lock`** - Lock file for reproducible dependency installation

## Code Conventions
- Python 3.12+ required
- Uses `ruff` for linting/formatting (configured in pyproject.toml with 88-char line length)
- Google-style docstrings enforced by ruff pydocstyle
- Conventional Commits for git messages (using commitizen)
- Type hints required (Pydantic models, function signatures)
- Error handling with specific exception types and user-friendly messages
- Uses hatchling as build backend with wheel packaging

## Important Notes
- SSH password automation uses `pexpect` and handles signal-based process termination
- Remote path validation prevents local directory operations on remote paths
- All rsync operations support `--dry-run` for preview mode
- The codebase has existing GEMINI.md with additional AI assistant guidelines
- Documentation is built with MkDocs Material theme and includes API references
- Version management is automated with commitizen (currently v0.4.1)
- Assets directory contains template files for configuration and environment setup

## Test Coverage Status
- **Overall Coverage**: 87% (Target: 83%+) ✅ **EXCEEDED**
- **High-Priority Modules**: All error scenarios comprehensively tested
  - **cli.py**: 99% - Command error scenarios
  - **generator.py**: 92% - Config file generation
  - **reader.py**: 89% - Configuration validation
  - **gear.py**: 88% - SSH automation with pexpect
  - **fetcher.py**: 85% - SSH authentication and error handling
  - **backuper.py**: 83% - Operation failure scenarios
  - **config.py**: 79% - Data model validation
  - **env.py**: 68% - Environment variable handling

## Integration Testing Infrastructure
- **Complete Integration Test Suite**: `tests/test_integration.py` (540 lines, 23 tests)
- **Test Success Rate**: 100% (23/23 tests passing)
- **Test Categories**:
  - **CLI Workflow Integration**: 7 tests covering init → status → fetch/backup/sync workflows
  - **Multi-Module Integration**: 6 tests verifying config → reader → gear → operation flows
  - **Sync Workflow Integration**: 6 tests for complete fetch-then-backup sequences
  - **End-to-End Integration**: 2 tests simulating realistic user workflows
  - **Infrastructure Fixtures**: 2 tests ensuring test framework reliability
- **Testing Strategy**: External dependency isolation, strategic mocking, deterministic test environments
- **Key Features**: Complete workflow validation, error propagation testing, configuration consistency verification


## Development Workflow

### Branch Development with Git Worktree

This project uses `git worktree` for isolated branch development to avoid conflicts and enable parallel development:

```bash
# Check available branches
git branch -a

# Create worktree for feature branch
git worktree add ../worktrees/<directory_name> <branch-name>
git worktree list

# Setup and develop in feature branch
cd ../worktrees/<directory_name>
uv venv
uv pip install -e .
# ... develop features ...

# Run tests and format code
task pytest
task format
task pre-commit

# Finish development
git add <files>
git commit
git merge origin/main
git push

# Clean up after merge
cd ../../fnb
git fetch --prune
git pull
git branch -d <branch_name>
git worktree remove ../worktrees/<directory_name>
```


### GitLab Issue and MR Integration

This project follows GitLab's issue-driven development workflow using the `glab` CLI tool:

#### Issue Management

```bash
# List and search issues
glab issue list                              # List all open issues
glab issue list --all                        # List all issues (open/closed)
glab issue list --assignee @me               # List issues assigned to you
glab issue list --search "SEARCH_WORD"       # Search issues by keyword
glab issue list --label "bug,enhancement"    # Filter by labels

# View and interact with issues
glab issue view <issue-number>               # View detailed issue information
glab issue view <issue-number> --web         # Open issue in web browser
glab issue note <id> --message "comment"     # Add comment to issue
glab issue note <id>                         # Add comment via editor

# Create and update issues
glab issue create                            # Create new issue (interactive)
glab issue create --title "title" --description "desc"
glab issue update <id> --title "new title"  # Update issue title
glab issue update <id> --description "desc" # Update issue description
glab issue update <id> --assignee @username # Assign issue to user
glab issue update <id> --label "bug,high"   # Add/update labels

# Issue state management
glab issue close <id>                        # Close issue
glab issue reopen <id>                       # Reopen closed issue
glab issue delete <id>                       # Delete issue
glab issue subscribe <id>                    # Subscribe to issue notifications
glab issue unsubscribe <id>                  # Unsubscribe from issue notifications
```

#### Merge Request (MR) Management

```bash
# List and view MRs
glab mr list                                 # List open merge requests
glab mr list --state all                     # List all MRs (open/closed/merged)
glab mr list --assignee @me                  # List MRs assigned to you
glab mr view <mr-number>                     # View MR details
glab mr view <mr-number> --web               # Open MR in web browser

# Create MRs
glab mr create                               # Create MR (interactive)
glab mr create --title "feat: add feature" --description "Closes #123"
glab mr create --draft                       # Create draft MR
glab mr create --target-branch develop      # Specify target branch

# MR interactions
glab mr note <mr-number> --message "comment" # Add comment to MR
glab mr approve <mr-number>                  # Approve MR
glab mr merge <mr-number>                    # Merge MR
glab mr close <mr-number>                    # Close MR without merging
glab mr reopen <mr-number>                   # Reopen closed MR
glab mr revoke <mr-number>                   # Revoke approval on MR
glab mr delete <mr-number>                   # Delete MR
glab mr subscribe <mr-number>                # Subscribe to MR notifications
glab mr unsubscribe <mr-number>              # Unsubscribe from MR notifications

# MR status and checks
glab mr view <mr-number>                     # View MR details
glab mr diff <mr-number>                     # Show diff for MR
glab mr checkout <mr-number>                 # Checkout MR branch locally
```

#### Development Workflow Integration

```bash
# Create branch for issue (use descriptive name based on issue)
git worktree add ../worktrees/<issue-branch-name> -b <issue-branch-name>

# Work on the issue in isolated environment
cd ../worktrees/<issue-branch-name>
uv venv
uv pip install -e .
# ... implement features/fixes ...

# Run development workflow
task pytest
task format
task pre-commit

# Create merge request when ready
glab mr create --title "fix: <issue-description>" --description "Closes #<issue-number>"

# Monitor MR status
glab mr view                                 # Check current branch MR status
glab mr view --web                           # Open MR in browser for review

# After MR review and approval
glab mr merge                                # Merge when ready
# Clean up worktree (see worktree workflow above)
```

#### Advanced glab Features

```bash
# Repository information
glab repo view                               # View repository information
glab repo view --web                         # Open repository in browser
glab repo clone <group/project>              # Clone repository

# Pipeline management (CI/CD)
glab ci list                                 # List recent pipelines
glab ci status                               # Show pipeline status for current commit
glab ci view <pipeline-id>                   # View specific pipeline details
glab ci run                                  # Create or run a new pipeline
glab ci cancel <pipeline-id>                 # Cancel a running pipeline

# Release management
glab release list                            # List releases
glab release view <tag>                      # View specific release
glab release create <tag>                    # Create new release

# Configuration and authentication
glab auth status                             # Check authentication status
glab config list                             # Show current configuration
glab config set editor vim                   # Set preferred editor
glab config set browser firefox             # Set preferred browser
```

#### Milestone and Issue Management

GitLab provides milestone functionality through the Web UI, but the `glab` CLI does not include milestone commands. Use the following approaches to manage milestones and grouped issues:

##### Creating Milestones

**Method 1: GitLab Web UI (Recommended)**
1. Navigate to GitLab Web UI → Project → Issues → Milestones
2. Click "New milestone"
3. Set title, description, and due date

**Method 2: Pseudo-milestones with Issue Labels**
```bash
# Group issues with common labels
glab issue create --label "milestone::pypi-v1.0,priority::high" --title "..."

# List milestone-related issues
glab issue list --label "milestone::pypi-v1.0"
```

##### Best Practices for Phase-based Issue Creation

**1. Planning Phase**
- Break large features into manageable phases
- Set priority levels for each phase (High, Medium, Low)
- Define clear dependencies between issues

```
<!-- Template for milestone -->
# Phase1: title
- Task1: title1 (issue #N)
  - breakdown1
  - breakdown2
- Task2: title2 (issue #N)
  - breakdown1

# Phase2: title
- Task3: title3 (issue #N)
  - breakdown1
  - breakdown2
  - breakdown2
- Task4: title4 (issue #N)
  - breakdown2
  - breakdown2
```

**2. Issue Creation Template**
```bash
glab issue create \
  --title "feat: feature name" \
  --description "$(cat <<'EOF'
## Overview
Feature description

## Implementation Tasks
- [ ] Task 1
- [ ] Task 2

## Acceptance Criteria
- Criteria 1
- Criteria 2

## Priority
High/Medium/Low

## Related
Milestone Name - Phase Name
EOF
)" \
  --label "enhancement,priority::high,milestone::name"
```

**3. Progress Tracking**
```bash
# Check active milestone issues
glab issue list --assignee @me --label "milestone::pypi-v1.0"

# Review completed issues
glab issue list --state closed --label "milestone::pypi-v1.0"

# Filter by phase and priority
glab issue list --label "milestone::pypi-v1.0,priority::high"
```

**4. Milestone Workflow Example**
```bash
# Create phase-based issues for PyPI deployment
glab issue create --title "feat: PyPI account setup" --label "milestone::pypi-v1.0,phase::preparation,priority::high"
glab issue create --title "feat: Package build environment" --label "milestone::pypi-v1.0,phase::build,priority::high"
glab issue create --title "feat: Production deployment" --label "milestone::pypi-v1.0,phase::deployment,priority::medium"

# Monitor milestone progress
glab issue list --label "milestone::pypi-v1.0" --state all
```

**Development Guidelines:**
- Always reference issue numbers in commit messages and MR descriptions
- Use `Closes #<issue-number>` in MR descriptions to auto-close issues
- Follow the existing issue labels and prioritization
- Create MRs for all changes, even small fixes
- Run all tests and pre-commit hooks before creating MR
- Use descriptive milestone labels for large feature sets
- Break down complex features into manageable, phased issues
- Maintain consistent labeling conventions across milestone issues

### Version Management

The project uses semantic versioning with commitizen and automated GitLab releases:

#### Standard Release Workflow
```bash
# Method 1: Manual step-by-step
task pytest
task format
task pre-commit
task bump-dry     # Preview version changes
task bump         # Execute version bump
task release      # Create GitLab release

# Method 2: Automated full workflow
task release-full  # Complete workflow in one command
```

**Available Taskfile Commands:**
- `task bump-dry` - Preview version bump with changelog
- `task bump` - Bump version and update changelog
- `task release` - Create GitLab release for current tag
- `task release-full` - Complete release workflow (test → bump → release)

#### Automated Version Management
- **Version files automatically updated:**
  - `pyproject.toml:version`
  - `src/fnb/__init__.py:__version__`
  - `CHANGELOG.md` with conventional commit history
- **Tag format:** Simple version number (e.g., `0.8.0`)
- **Changelog format:** Conventional commits with categorization (feat, fix, refactor, etc.)

#### GitLab Release Integration
```bash
# List existing releases
glab release list

# Create release with detailed notes
glab release create v1.0.0 \
  --name "fnb v1.0.0 - Production Ready" \
  --notes "$(cat CHANGELOG.md | head -20)"

# View release in browser
glab release view v1.0.0 --web
```

#### Version Scheme Configuration
```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.8.0"
tag_format = "$version"
version_scheme = "semver"
update_changelog_on_bump = true
major_version_zero = true
```

## Directory Structure Notes

- `src/fnb/`: Main Python package source code
- `src/fnb/assets/`: Template files for configuration and environment
- `tests/`: Test suite with pytest configuration
- `docs/`: MkDocs documentation site
- `examples/`: Example configuration files
- `uv.lock`: Lock file for reproducible dependency installation

## Common Gotchas

- Always use `uv run` for command execution to ensure correct Python environment
- SSH password automation with `pexpect` requires proper signal handling for clean termination
- Remote path validation prevents accidental local operations on remote filesystem paths
- Configuration discovery follows a specific order: local `fnb.toml` → `~/.config/fnb/config.toml` → platform paths
- All rsync operations require proper `options` field configuration in TOML

## DO

- Always respond in **Japanese**, except for code and docstrings.
- Use **English** for all code, comments, and docstrings.
- Output **one function / class at a time**, with explanation.
- Follow **Python (PEP8)** naming conventions (`snake_case` for variables/functions, `PascalCase` for classes)
- Use only predefined modules/functions unless approved.
- Insert `TODO` markers in docstrings when leaving suggestions for improvement.
- Follow **Conventional Commits** style in commit messages.
- Ask when unsure -- never assume functionality or structure.

## DONT

- Do not invent new functions, classes, arguments, or file structures.
- Do not use Japanese in code, comments, docstrings.
- Do not output multiple features or components in one response.
- Do not omit or remove `TODO` or existing discussion points.
- Do not write pseudocode unless explicitly asked.
- Do not change user-established naming, file organization, or conventions.

## Commit Rules

- Use **Conventional Commits** for all Git commit messages.
- Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Use scope where helpful (e.g., `fix(config): handle missing TOML sections`)
- For breaking changes, add `!` after type/scope
- **Do not** include links or email addresses in commit messages (attribution text without links is acceptable)
