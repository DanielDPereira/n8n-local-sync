# Integration Guide: Using n8n-local-sync in any Repository

This guide explains how to integrate `n8n-local-sync` into your existing n8n project repositories (e.g., alongside your `docker-compose.yml` or custom n8n nodes). Because `n8n-local-sync` follows standard GitOps principles, it operates seamlessly alongside your existing codebase without interfering with it.

## Step 1: Install the CLI

Ensure you have Python 3.9+ installed on your system. You should install `n8n-local-sync` globally so you can use the CLI from anywhere.

```bash
pip install n8n-local-sync
```

*(Tip: If you prefer to isolate python environments, we recommend using `pipx install n8n-local-sync`).*

## Step 2: Initialize the Project

Open your terminal and navigate to the **root of your repository** (for example, the same folder where your n8n `docker-compose.yml` file is located).

Run the initialization command:
```bash
n8n-sync init
```

This will automatically create:
1. An `n8n/workflows/` directory (where your JSON workflows will be saved).
2. A `.n8n-sync.yaml` file (your basic configuration).

## Step 3: Configure the Connection

Open the newly created `.n8n-sync.yaml` file. Verify that the `url` matches your n8n instance. The default is `http://localhost:5678`, which works perfectly if you are running n8n via local Docker.

Next, you need to authorize the CLI. **Create a `.env` file** in the root of your project (if it doesn't exist already) and add your n8n API Key (which you can generate in the n8n UI settings):

```env
N8N_API_KEY=your_api_key_here
```

> ⚠️ **Important:** Ensure that your `.env` file is listed in your repository's `.gitignore` file so you do not accidentally leak your API key to GitHub or GitLab.

## Step 4: The First "Pull" (Download Workflows)

To download all existing workflows from your n8n instance and save them locally:

```bash
n8n-sync export
# Alternatively, you can use: n8n-sync pull
```

This command populates the `n8n/workflows/` folder with clean, normalized `.json` files, named after their respective workflow IDs.

## Step 5: Save to Git

Now you return to your standard development workflow. Commit the new files to your repository:

```bash
git add .n8n-sync.yaml n8n/workflows/
git commit -m "chore: initial n8n workflow setup"
git push
```

---

## 🔄 Daily GitOps Workflow

Once integrated, your day-to-day process becomes straightforward.

**When you build/edit a workflow in the n8n UI (browser):**
```bash
n8n-sync pull
git add n8n/workflows/
git commit -m "feat: update sales automation workflow"
```

**When you pull the repository on another machine (or via CI/CD for deployment):**
```bash
# Push the local Git-versioned workflows to the running n8n instance
n8n-sync push
```

If multiple people edit the same workflow simultaneously in different environments, `n8n-local-sync` will detect the `CONFLICT` during push or pull and safely abort the operation, warning you before any work is overwritten!
