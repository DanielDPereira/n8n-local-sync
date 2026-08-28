<div align="center">
  <h1>🚀 n8n-local-sync</h1>
  <p><i>The definitive open-source CLI tool for versioning, validating, and syncing n8n workflows with Git.</i></p>

  [![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
</div>

---

## 📖 Overview

**n8n-local-sync** bridges the gap between your [n8n](https://n8n.io/) instances and Git. By treating your n8n workflows as code, you can leverage standard software engineering practices—like version control, peer reviews, CI/CD, and automated backups—for your automations.

### Key Features
* 🔄 **Bidirectional Syncing:** Seamlessly pull (`export`) and push (`import`) workflows using the official n8n REST API.
* 🛡️ **Validation & Security:** Catch invalid JSON structures and prevent accidental leakage of sensitive credentials (API keys, passwords, etc.) with built-in heuristic scanning.
* 🌲 **Git-Native:** Cleans workflow metadata (e.g., timestamps, volatile IDs) so that `git diff` remains clean, focusing only on meaningful structural changes.
* 🧪 **Dry-Run Mode:** Simulate changes (`--dry-run`) across all destructive commands before applying them.
* 🏷️ **Tag Filtering:** Target specific environments or modules during export using the `--tag` flag.
* 🤖 **CI/CD Ready:** Configure your environment dynamically using `.env` files or environment variables (e.g., `N8N_BASE_URL`), perfectly suited for CI pipelines.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* n8n instance (Version 0.164.0+ required to support the Public REST API)

### Installation

Clone the repository and install the CLI locally in editable mode (recommended for development):

```bash
git clone https://github.com/DanielDPereira/n8n-local-sync.git
cd n8n-local-sync
pip install -e .
```

### Authentication & Setup

1. **Initialize the project** in the directory where you want to store your workflows:
   ```bash
   n8n-sync init
   ```
   This will create a `.n8n-sync.yaml` configuration file and a default `n8n/workflows/` directory.

2. **Set up your environment variables**. Copy the provided example to `.env`:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and insert your n8n API Key (Generated in n8n -> Settings -> API):
   ```env
   N8N_API_KEY=your_api_key_here
   N8N_BASE_URL=http://localhost:5678  # Overrides the URL in .n8n-sync.yaml
   ```

---

## 🛠️ Command Line Interface

The `n8n-sync` tool provides an intuitive suite of commands for workflow lifecycle management.

### `init`
Initializes a new `n8n-local-sync` project in the current directory.
```bash
n8n-sync init
```
* **What it does:** Generates the `.n8n-sync.yaml` configuration file and creates the target workflow directory (default: `n8n/workflows`). Will fail safely if a configuration already exists.

### `export`
Pulls all workflows from the connected n8n instance and saves them locally as JSON files.
```bash
n8n-sync export [OPTIONS]
```
* **Options:**
  * `--dry-run`: Simulates the export process without writing any files to disk.
  * `--tag TEXT`: Only exports workflows that contain the specified tag (e.g., `--tag production`).
* **What it does:** Fetches workflows via the API, strips out volatile properties (like `createdAt` and `updatedAt`) to ensure clean Git history, and serializes them in a human-readable format.

### `import`
Pushes the local workflow JSON files back into the connected n8n instance.
```bash
n8n-sync import [OPTIONS]
```
* **Options:**
  * `--dry-run`: Simulates the import, showing what would be created or updated without actually making changes to the remote n8n instance.
* **What it does:** Reads local `.json` files, validates their schema structure, isolates allowed payload fields, and safely creates (`POST`) or updates (`PUT`) workflows on the n8n server.

### `sync`
Intelligently synchronizes differences between the local repository and the n8n instance.
```bash
n8n-sync sync [OPTIONS]
```
* **Options:**
  * `--dry-run`: Simulates the sync process without applying any modifications.
  * `--force`: Overwrites local modifications with the remote n8n versions, ignoring conflicts.
* **What it does:** Compares remote state with local state. Automatically pulls new remote workflows. Warns if it detects conflicts where a file has diverged (unless `--force` is used).

### `validate`
Performs static analysis on the local workflows to ensure structural integrity and security.
```bash
n8n-sync validate
```
* **What it does:** Parses local workflow files to verify valid JSON formatting, enforces required fields (`name`, `nodes`, `connections`), and scans text values for potential secrets or hardcoded API keys. This is automatically run in the pre-commit hook.

### `status`
Displays a quick overview of the current synchronization state.
```bash
n8n-sync status
```
* **What it does:** Compares local workflow files with the remote server state and summarizes missing files, untracked remote workflows, and diverged files.

### `diff`
Shows a detailed visual difference between a local workflow and its remote counterpart.
```bash
n8n-sync diff
```
* **What it does:** Pulls the remote state and generates a patch-like terminal diff output to highlight exactly what node parameters or connections have changed.

---

## 🔒 Security Best Practices

We treat security as a first-class citizen:

1. **No Credentials in Code:** Your `N8N_API_KEY` stays in your local `.env` file. Ensure `.env` is listed in your `.gitignore`.
2. **Pre-commit Hooks:** Prevent bad code from entering your repository. We bundle a pre-commit hook that runs `n8n-sync validate`.
   ```bash
   pip install pre-commit
   pre-commit install
   ```
3. **Payload Sanitization:** The CLI deliberately drops metadata and strips keys that should not be transmitted to the n8n `/api/v1/workflows` endpoints, keeping both the API and your repository clean.

---

## 🤝 Contributing

We welcome community contributions! Please read our [AGENTS.md](AGENTS.md) for architectural guidelines, setup your development environment with `pytest`, and ensure your code complies with `black` and `ruff`.

## 📄 License

This project is licensed under the MIT License.
