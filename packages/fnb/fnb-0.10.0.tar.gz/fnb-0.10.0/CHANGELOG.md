## 0.9.1-test (2025-08-21)

### Feat

- enhance TestPyPI verification task with detailed checks (issue#17)
- implement automatic TestPyPI deployment on tag push (issue#17)
- add verify:testpypi task for automated TestPyPI verification

### Fix

- correct VERSION parameter handling in verify:testpypi task

### Refactor

- complete Phase 5 - testing and validation
- complete Phase 4 - configuration updates for new test structure
- update Taskfile.yml test tasks for new directory structure
- update pytest configuration for new test structure
- complete Phase 3 - move test_integration.py to tests/integration/
- complete Phase 2 - move remaining test files to tests/unit/
- move test_fixtures.py to tests/unit/ directory
- move test_generator.py to tests/unit/ directory
- move test_env.py to tests/unit/ directory
- move test_config.py to tests/unit/ directory

## 0.9.0 (2025-08-21)

### Feat

- add deploy stages for TestPyPI and PyPI
- add build stage for package creation in CI/CD
- add CI/CD and integration testing tasks to Taskfile
- add version management tasks to Taskfile

### Refactor

- reorganize Taskfile with improved naming and structure
- remove go-task-bin dependency from CI/CD
- remove redundant CI jobs for pipeline efficiency
- modernize GitLab CI/CD syntax from only to rules
- remove obsolete sandbox task from Taskfile

## 0.8.0 (2025-08-20)

### Feat

- complete PyPI metadata configuration

## 0.7.0 (2025-08-20)

### Feat

- add PyPI/TestPyPI publish tasks to Taskfile

### Fix

- remove duplicate file inclusion in wheel build

## 0.6.1 (2025-08-20)

### Fix

- handle pexpect.interact() failure in non-interactive environments

## 0.6.0 (2025-08-20)

### Feat

- add manual test Taskfile for controlled server testing
- add tests/manual/ to .gitignore
- remove integration tests directory

## 0.5.0 (2025-08-19)

### Feat

- **task**: add GitLab repository and pages navigation tasks
- **fnb**: rename project from rfb to fnb (fetch and backup)

### Fix

- **integration**: resolve failing tests and achieve 100% success rate
- **tests**: resolve environment variable interference between test modules
- **env**: correct environment variable prefix from RFB_ to FNB_
- **test**: improve testing of sys.exit in generator

### Refactor

- finalize rfb to fnb rename across all modules
- **reader**: update ConfigReader to use FnbConfig and fnb path
- **config**: rename RfbConfig to FnbConfig throughout codebase
- **fnb**: rename all references from rfb to fnb

## 0.4.1 (2025-07-25)

### Fix

- **task**: added Taskfile

## 0.4.0 (2025-05-07)

### Feat

- **init**: include timestamped header comment in generated files

### Fix

- **env.sampl**: fixed the instruction to run dotenvx

## 0.3.1 (2025-04-21)

### Fix

- **cli**: changed sync options default
- **gear**: make SSH error handling more flexible for common signals

### Refactor

- **config**: migrate to platformdirs for XDG compliant paths
- **paths**: ensure consistent use of Path objects
- improve type annotations consistency and standardize docstrings

## 0.3.0 (2025-04-18)

### Feat

- **auth**: implement SSH password retrieval from environment variables
- **config**: add .env file support for SSH password management
- **cli**: fixed default options to production mode
- **config**: add embedded config template in assets directory
- **gear**: add verify_directory function
- **cli**: added rfb version to show version number

### Refactor

- **create_dirs**: replace ensure_directory_exists with verify_directory

## 0.2.0 (2025-04-17)

### Feat

- **cli**: add ssh-password option to fetch command
- **status**: feat: improve status display with proper rsync paths
- **gear**: feat: add directory existence verification before rsync operations
- **cli**: Implement robust sync command for combined fetch and backup
- **cli**: add status command to display configuration state
- **cli**: implement `rfb init` command for config generation
- **init**: add config file generator module
- **backup**: implement backup logic with rsync
- **fetch**: implement fetch logic with rsync and optional SSH password
- **cli**: implement fetch command using ConfigReader
- **cli**: add base CLI with fetch/backup/sync commands
- **core**: implement fetcher and backuper logic with label support
- **gear**: add rsync utility with optional password automation
- **cli**: implement initial CLI entry point using Typer
- **config**: implement config loader with support for .env, XDG paths, and file merging
- **rfb**: Initial commit

### Fix

- **reader**: fix: preserve tilde and original path format in status display
- **init**: temporal fix
- **pyproject.toml**: updated project information

### Refactor

- **gear**: Refactor gear.py for better password handling and readability
- **config**: split config model and reader logic into separate classes
